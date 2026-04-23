from app.services.graph_builder import graph_builder
import time

class GapAnalyzerService:

    def calculate_research_metrics(self):
        """Calculates CAS and PIS with query latency tracking."""
        t_start = time.perf_counter()

        with graph_builder.driver.session() as session:
            t_cas = time.perf_counter()
            cas_result = session.run("""
                MATCH (s:Skill) WHERE s.demand_count > 0
                WITH sum(s.demand_count) AS total_demand
                MATCH (covered:Skill)
                WHERE ()-[:COVERS]->(covered) AND covered.demand_count > 0
                WITH total_demand, sum(covered.demand_count) AS covered_demand
                RETURN total_demand, covered_demand,
                       round(toFloat(covered_demand) / total_demand * 100, 2) AS cas_score
            """).single()
            cas_latency_ms = round((time.perf_counter() - t_cas) * 1000, 2)

            t_pis = time.perf_counter()
            pis_result = session.run("""
                MATCH (c:Course)-[:COVERS]->(advanced:Skill)
                MATCH (prereq:Skill)-[:LEADS_TO]->(advanced)
                WITH count(*) AS total_chains
                MATCH (c:Course)-[:COVERS]->(advanced:Skill)
                MATCH (prereq:Skill)-[:LEADS_TO]->(advanced)
                WHERE NOT ()-[:COVERS]->(prereq)
                WITH total_chains, count(*) AS broken_chains
                RETURN total_chains, broken_chains,
                       CASE WHEN total_chains = 0 THEN 100.0
                       ELSE round(100.0 - (toFloat(broken_chains) / total_chains * 100), 2)
                       END AS pis_score
            """).single()
            pis_latency_ms = round((time.perf_counter() - t_pis) * 1000, 2)

        total_latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        return {
            "curriculum_alignment_score_percent":  cas_result["cas_score"]  if cas_result else 0,
            "pedagogical_integrity_score_percent": pis_result["pis_score"]  if pis_result else 100,
            "stats": {
                "total_market_demand_points":  cas_result["total_demand"]   if cas_result else 0,
                "covered_demand_points":       cas_result["covered_demand"] if cas_result else 0,
                "total_prerequisite_chains":   pis_result["total_chains"]   if pis_result else 0,
                "broken_chains":               pis_result["broken_chains"]  if pis_result else 0,
            },
            "query_latency_ms": {
                "cas_query":    cas_latency_ms,
                "pis_query":    pis_latency_ms,
                "total":        total_latency_ms,
                "nfr01_target": 5000,
                "nfr01_passed": total_latency_ms < 5000
            }
        }

    def get_prioritized_gaps(self, limit: int = 10):
        """Ranks missing skills by Market Demand + Structural Importance."""
        t_start = time.perf_counter()

        with graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (s:Skill)
                WHERE NOT ()-[:COVERS]->(s) AND s.demand_count > 0
                OPTIONAL MATCH (s)-[:LEADS_TO]->(dependent:Skill)
                WITH s, count(dependent) AS bottleneck_weight
                WITH s.name         AS missing_skill,
                     s.demand_count AS market_demand,
                     bottleneck_weight,
                     (s.demand_count + (bottleneck_weight * 5)) AS priority_score
                RETURN missing_skill, market_demand, bottleneck_weight, priority_score
                ORDER BY priority_score DESC
                LIMIT $limit
            """, limit=limit)
            gaps = [dict(r) for r in result]

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        print(f"⏱️  get_prioritized_gaps latency: {latency_ms}ms")
        return gaps

    def get_prioritized_gaps_hybrid(self, limit: int = 10) -> list[dict]:
        """
        Hybrid scoring: Graph priority + semantic similarity boost.

        For each gap, checks if semantically similar skills ARE covered
        by the syllabus. If similar covered skills exist, the gap gets
        a semantic_coverage_score — meaning the curriculum partially
        addresses this topic under a different name.

        This is the Graph-RAG + Embeddings approach described in the paper.
        Falls back to graph-only if embeddings not built yet.
        """
        from app.services.vector_store import vector_store

        # Check if embeddings exist
        stats = vector_store.get_index_stats()
        if not stats["index_ready"]:
            print("⚠️  Embeddings not built yet — falling back to graph-only scoring.")
            return self.get_prioritized_gaps(limit=limit)

        t_start = time.perf_counter()

        # 1. Get graph-based gaps (larger pool to re-rank)
        with graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (s:Skill)
                WHERE NOT ()-[:COVERS]->(s) AND s.demand_count > 0
                OPTIONAL MATCH (s)-[:LEADS_TO]->(dependent:Skill)
                WITH s, count(dependent) AS bottleneck_weight
                WITH s.name         AS missing_skill,
                     s.demand_count AS market_demand,
                     bottleneck_weight,
                     (s.demand_count + (bottleneck_weight * 5)) AS graph_score
                RETURN missing_skill, market_demand, bottleneck_weight, graph_score
                ORDER BY graph_score DESC
                LIMIT $limit
            """, limit=limit * 3)  # Fetch 3x to allow re-ranking
            candidates = [dict(r) for r in result]

        # 2. Get covered skill names for semantic comparison
        with graph_builder.driver.session() as session:
            covered_result = session.run("""
                MATCH ()-[:COVERS]->(s:Skill)
                RETURN DISTINCT s.name AS name
            """)
            covered_skills = {r["name"] for r in covered_result}

        # 3. For each candidate gap, compute semantic coverage score
        enriched = []
        for gap in candidates:
            skill_name = gap["missing_skill"]

            # Find semantically similar skills
            similar = vector_store.get_similar_skills(
                skill_name, top_k=5, min_similarity=0.5
            )

            # Check how many similar skills are covered
            covered_similar  = [s for s in similar if s["name"] in covered_skills]
            max_sim_covered  = max((s["similarity"] for s in covered_similar), default=0)

            # Hybrid score: graph_score boosted if NOT semantically covered
            # High semantic coverage = curriculum partially covers this → lower urgency
            semantic_penalty = max_sim_covered * 0.3  # reduce score if similar covered
            hybrid_score     = gap["graph_score"] * (1 - semantic_penalty)

            enriched.append({
                **gap,
                "hybrid_score":         round(hybrid_score, 2),
                "semantic_coverage":    round(max_sim_covered, 4),
                "similar_covered":      [s["name"] for s in covered_similar],
                "scoring_method":       "hybrid"
            })

        # 4. Re-rank by hybrid score and return top limit
        enriched.sort(key=lambda x: x["hybrid_score"], reverse=True)
        result = enriched[:limit]

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        print(f"⏱️  get_prioritized_gaps_hybrid latency: {latency_ms}ms")

        return result

    def get_insertion_recommendations(self, missing_skill_name: str):
        """Recommends best existing course to inject a missing skill."""
        t_start = time.perf_counter()

        with graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (missing:Skill {name: $skill_name})<-[:REQUIRES]-(j:Job)-[:REQUIRES]->(peer:Skill)
                MATCH (c:Course)-[:COVERS]->(peer)
                RETURN c.name      AS recommended_course,
                       count(peer) AS affinity_score,
                       collect(DISTINCT peer.name)[0..5] AS overlapping_context
                ORDER BY affinity_score DESC
                LIMIT 3
            """, skill_name=missing_skill_name)
            recommendations = [dict(r) for r in result]

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        print(f"⏱️  get_insertion_recommendations('{missing_skill_name}') "
              f"latency: {latency_ms}ms")
        return recommendations

    def get_full_latency_report(self):
        """Runs all major queries and returns latency report for NFR validation."""
        print("📊 Running full latency benchmark...")
        report = {}

        t = time.perf_counter()
        self.calculate_research_metrics()
        report["metrics_query_ms"] = round((time.perf_counter() - t) * 1000, 2)

        t = time.perf_counter()
        gaps = self.get_prioritized_gaps(limit=10)
        report["gap_priority_query_ms"] = round((time.perf_counter() - t) * 1000, 2)

        if gaps:
            t = time.perf_counter()
            self.get_insertion_recommendations(gaps[0]["missing_skill"])
            report["recommendation_query_ms"] = round((time.perf_counter() - t) * 1000, 2)

        t = time.perf_counter()
        with graph_builder.driver.session() as session:
            session.run("""
                MATCH path = (s:Skill)-[:LEADS_TO*1..3]->(target:Skill)
                RETURN s.name, target.name, length(path) AS hops
                LIMIT 100
            """)
        report["three_hop_traversal_ms"] = round((time.perf_counter() - t) * 1000, 2)

        report["nfr01_passed"] = report["metrics_query_ms"] < 5000
        report["nfr03_passed"] = report["three_hop_traversal_ms"] < 500

        print(f"✅ Latency benchmark complete: {report}")
        return report

gap_analyzer = GapAnalyzerService()
