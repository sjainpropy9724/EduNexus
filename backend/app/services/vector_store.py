"""
Vector Store — EduNexus V2
===========================
Embeds all Skill nodes using sentence-transformers (all-MiniLM-L6-v2).
Stores embeddings as a property on Skill nodes in Neo4j.
Used by gap_analyzer.py for semantic similarity scoring.

One-time setup:
    python -c "from app.services.vector_store import vector_store; vector_store.build_index()"

Or via API:
    POST /api/v1/graph/build_embeddings
"""

import json
import time
import numpy as np
from app.services.graph_builder import graph_builder

MODEL_NAME = "all-MiniLM-L6-v2"  # 80MB, runs on CPU, no API needed

class VectorStoreService:

    def __init__(self):
        self._model = None  # Lazy load — don't load at import time

    def _get_model(self):
        """Lazy-loads the sentence transformer model."""
        if self._model is None:
            print(f"⏳ Loading sentence-transformer model ({MODEL_NAME})...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(MODEL_NAME)
            print("✅ Model loaded.")
        return self._model

    def build_index(self, batch_size: int = 256) -> dict:
        """
        Embeds all Skill nodes and stores vectors in Neo4j.
        Run once after data ingestion, re-run after major graph updates.
        """
        print("\n🔧 Building semantic index...")
        t_start = time.perf_counter()

        # 1. Fetch all skill names from Neo4j
        with graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (s:Skill)
                WHERE s.name IS NOT NULL
                RETURN s.name AS name
                ORDER BY s.name
            """)
            skills = [r["name"] for r in result]

        print(f"  Skills to embed: {len(skills)}")

        if not skills:
            return {"status": "error", "message": "No skills found in graph"}

        # 2. Generate embeddings in batches
        model = self._get_model()
        print(f"  Generating embeddings (batch_size={batch_size})...")

        t_embed = time.perf_counter()
        embeddings = model.encode(
            skills,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2 normalize for cosine similarity
        )
        embed_time = round((time.perf_counter() - t_embed) * 1000, 2)
        print(f"  Embedding time: {embed_time}ms")

        # 3. Store embeddings back into Neo4j as JSON strings
        print("  Storing embeddings in Neo4j...")
        t_store = time.perf_counter()

        batch_data = [
            {
                "name":      skill,
                "embedding": json.dumps(embeddings[i].tolist())
            }
            for i, skill in enumerate(skills)
        ]

        with graph_builder.driver.session() as session:
            # Process in chunks to avoid memory issues
            chunk_size = 500
            for i in range(0, len(batch_data), chunk_size):
                chunk = batch_data[i:i + chunk_size]
                session.run("""
                    UNWIND $batch AS item
                    MATCH (s:Skill {name: item.name})
                    SET s.embedding = item.embedding
                """, batch=chunk)
                print(f"  Stored {min(i + chunk_size, len(batch_data))}"
                      f"/{len(skills)} embeddings...")

        store_time  = round((time.perf_counter() - t_store) * 1000, 2)
        total_time  = round((time.perf_counter() - t_start) * 1000, 2)

        print(f"\n✅ Semantic index built!")
        print(f"   Skills embedded:  {len(skills)}")
        print(f"   Embedding time:   {embed_time}ms")
        print(f"   Storage time:     {store_time}ms")
        print(f"   Total time:       {total_time}ms")

        return {
            "status":          "success",
            "skills_embedded": len(skills),
            "embed_time_ms":   embed_time,
            "store_time_ms":   store_time,
            "total_time_ms":   total_time
        }

    def get_similar_skills(self,
                           query_skill: str,
                           top_k: int = 5,
                           min_similarity: float = 0.5) -> list[dict]:
        """
        Finds semantically similar skills to a given skill name.
        Used by gap_analyzer for hybrid scoring.

        Returns list of {name, similarity} dicts.
        """
        model = self._get_model()

        # Encode the query
        query_vec = model.encode(
            [query_skill],
            normalize_embeddings=True,
            convert_to_numpy=True
        )[0]

        # Fetch all stored embeddings
        with graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (s:Skill)
                WHERE s.embedding IS NOT NULL
                  AND s.name <> $query
                RETURN s.name AS name, s.embedding AS embedding
            """, query=query_skill)

            candidates = [(r["name"], r["embedding"]) for r in result]

        if not candidates:
            return []

        # Compute cosine similarities
        names      = [c[0] for c in candidates]
        embeddings = np.array([json.loads(c[1]) for c in candidates])

        similarities = embeddings @ query_vec  # dot product (vectors are L2 normalized)

        # Get top-k above threshold
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            sim = float(similarities[idx])
            if sim >= min_similarity:
                results.append({
                    "name":       names[idx],
                    "similarity": round(sim, 4)
                })

        return results

    def get_index_stats(self) -> dict:
        """Returns stats about the current embedding index."""
        with graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (s:Skill)
                RETURN
                    count(s) AS total_skills,
                    count(s.embedding) AS embedded_skills
            """).single()

        total    = result["total_skills"]
        embedded = result["embedded_skills"]

        return {
            "total_skills":    total,
            "embedded_skills": embedded,
            "coverage_pct":    round(embedded / total * 100, 2) if total > 0 else 0,
            "index_ready":     embedded > 0
        }

vector_store = VectorStoreService()
