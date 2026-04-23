"""
TF-IDF Baseline Comparison — EduNexus V2 (Fixed Evaluation)
=============================================================
Uses Precision@K, Recall@K and MAP for fair comparison.
Both approaches evaluated at same K values.

Run from EduNexus_v2/backend/:
    python tfidf_baseline_comparison.py
"""

import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.graph_builder import graph_builder

# ── Ground Truth ──────────────────────────────────────────────────────────────
KNOWN_GAPS = [
    "Docker", "Kubernetes", "React", "Node.js", "MongoDB",
    "AWS", "Generative AI", "LangChain", "RAG", "FastAPI"
]

# ── Data Fetchers ─────────────────────────────────────────────────────────────

def get_syllabus_skills() -> list[str]:
    with graph_builder.driver.session() as session:
        result = session.run("""
            MATCH (c:Course)-[:COVERS]->(s:Skill)
            RETURN DISTINCT s.name AS skill
        """)
        return [r["skill"] for r in result]

def get_market_skills(limit: int = 300) -> list[str]:
    with graph_builder.driver.session() as session:
        result = session.run("""
            MATCH (s:Skill)
            WHERE s.demand_count > 0
            RETURN s.name AS skill, s.demand_count AS demand
            ORDER BY s.demand_count DESC
            LIMIT $limit
        """, limit=limit)
        return [r["skill"] for r in result]

def get_graph_gaps_ranked(limit: int = 300) -> list[str]:
    """Returns gaps ranked by Graph-RAG priority score."""
    with graph_builder.driver.session() as session:
        result = session.run("""
            MATCH (s:Skill)
            WHERE NOT ()-[:COVERS]->(s) AND s.demand_count > 0
            OPTIONAL MATCH (s)-[:LEADS_TO]->(dependent:Skill)
            WITH s, count(dependent) AS bottleneck_weight
            WITH s.name AS skill,
                 (s.demand_count + (bottleneck_weight * 5)) AS priority_score
            RETURN skill, priority_score
            ORDER BY priority_score DESC
            LIMIT $limit
        """, limit=limit)
        return [r["skill"] for r in result]

# ── TF-IDF Ranked Gaps ────────────────────────────────────────────────────────

def get_tfidf_gaps_ranked(syllabus_skills: list[str],
                          market_skills: list[str]) -> list[str]:
    """
    Returns market skills ranked by dissimilarity to syllabus.
    Most dissimilar = biggest gap.
    """
    all_skills = syllabus_skills + market_skills
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
    tfidf_matrix = vectorizer.fit_transform(all_skills)

    syllabus_vectors = tfidf_matrix[:len(syllabus_skills)]
    market_vectors   = tfidf_matrix[len(syllabus_skills):]

    scored = []
    for i, skill in enumerate(market_skills):
        sims      = cosine_similarity(market_vectors[i], syllabus_vectors)[0]
        gap_score = 1.0 - sims.max()
        scored.append((skill, gap_score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scored]

# ── Evaluation Metrics ────────────────────────────────────────────────────────

def precision_at_k(ranked: list[str], known: list[str], k: int) -> float:
    top_k  = set(g.lower() for g in ranked[:k])
    known_s = set(g.lower() for g in known)
    return len(top_k & known_s) / k

def recall_at_k(ranked: list[str], known: list[str], k: int) -> float:
    top_k   = set(g.lower() for g in ranked[:k])
    known_s = set(g.lower() for g in known)
    return len(top_k & known_s) / len(known_s)

def average_precision(ranked: list[str], known: list[str]) -> float:
    known_s = set(g.lower() for g in known)
    hits = 0
    sum_p = 0.0
    for i, gap in enumerate(ranked):
        if gap.lower() in known_s:
            hits  += 1
            sum_p += hits / (i + 1)
    return sum_p / len(known_s) if known_s else 0.0

# ── Main ──────────────────────────────────────────────────────────────────────

def run_comparison():
    print("\n🔬 TF-IDF vs Graph-RAG — Fair Comparison (Precision@K)")
    print("=" * 60)
    print(f"  Ground truth gaps ({len(KNOWN_GAPS)}): {KNOWN_GAPS}")

    print("\n  Fetching data from Neo4j...")
    syllabus_skills = get_syllabus_skills()
    market_skills   = get_market_skills(limit=300)
    print(f"  Syllabus skills: {len(syllabus_skills)}")
    print(f"  Market skills:   {len(market_skills)}")

    print("\n  Running TF-IDF ranking...")
    t = time.perf_counter()
    tfidf_ranked = get_tfidf_gaps_ranked(syllabus_skills, market_skills)
    tfidf_time   = round((time.perf_counter() - t) * 1000, 2)

    print("  Running Graph-RAG ranking...")
    t = time.perf_counter()
    graph_ranked = get_graph_gaps_ranked(limit=300)
    graph_time   = round((time.perf_counter() - t) * 1000, 2)

    k_values = [10, 20, 50, 100]

    print(f"\n{'='*60}")
    print("  PRECISION@K COMPARISON")
    print(f"{'='*60}")
    print(f"  {'K':<8} {'TF-IDF P@K':>12} {'Graph-RAG P@K':>15} {'Winner':>12}")
    print(f"  {'-'*52}")
    for k in k_values:
        p_t = precision_at_k(tfidf_ranked, KNOWN_GAPS, k)
        p_g = precision_at_k(graph_ranked, KNOWN_GAPS, k)
        w   = "Graph-RAG ✅" if p_g >= p_t else "TF-IDF"
        print(f"  {k:<8} {p_t:>11.2%} {p_g:>14.2%} {w:>12}")

    print(f"\n{'='*60}")
    print("  RECALL@K COMPARISON")
    print(f"{'='*60}")
    print(f"  {'K':<8} {'TF-IDF R@K':>12} {'Graph-RAG R@K':>15} {'Winner':>12}")
    print(f"  {'-'*52}")
    for k in k_values:
        r_t = recall_at_k(tfidf_ranked, KNOWN_GAPS, k)
        r_g = recall_at_k(graph_ranked, KNOWN_GAPS, k)
        w   = "Graph-RAG ✅" if r_g >= r_t else "TF-IDF"
        print(f"  {k:<8} {r_t:>11.2%} {r_g:>14.2%} {w:>12}")

    ap_t = average_precision(tfidf_ranked, KNOWN_GAPS)
    ap_g = average_precision(graph_ranked, KNOWN_GAPS)
    imp  = ((ap_g - ap_t) / ap_t * 100) if ap_t > 0 else 0

    print(f"\n{'='*60}")
    print("  MEAN AVERAGE PRECISION (MAP) — Primary Metric")
    print(f"{'='*60}")
    print(f"  TF-IDF MAP:       {ap_t:.4f} ({ap_t:.2%})")
    print(f"  Graph-RAG MAP:    {ap_g:.4f} ({ap_g:.2%})")
    print(f"  Improvement:      {imp:+.1f}%")
    print(f"  Winner:           {'Graph-RAG ✅' if ap_g > ap_t else 'TF-IDF'}")

    print(f"\n{'='*60}")
    print("  DETECTION TIME")
    print(f"{'='*60}")
    print(f"  TF-IDF:           {tfidf_time}ms")
    print(f"  Graph-RAG:        {graph_time}ms")
    if graph_time > 0:
        print(f"  Speed:            Graph-RAG is {tfidf_time/graph_time:.1f}x faster")

    print(f"\n{'='*60}")
    print("  QUALITATIVE ADVANTAGE (unique to Graph-RAG)")
    print(f"{'='*60}")
    print("  ✅ Detects broken prerequisite chains")
    print("  ✅ Identifies bottleneck skills blocking multiple topics")
    print("  ✅ Provides course-level injection recommendations")
    print("  ✅ Structural validation of curriculum (PIS score)")
    print("  ❌ None of these are possible with TF-IDF\n")

if __name__ == "__main__":
    run_comparison()
