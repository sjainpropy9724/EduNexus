"""
One-time cleanup script — run ONCE after placing skill_normalizer.py.
Merges duplicate Skill nodes in the existing V2 graph.

Run from EduNexus_v2/backend/:
    python cleanup_duplicates.py
"""

from app.services.graph_builder import graph_builder
from app.services.skill_normalizer import SKILL_ALIASES, normalize

def cleanup_duplicate_skills():
    print("🧹 Starting duplicate skill cleanup...")
    merged_count = 0

    with graph_builder.driver.session() as session:
        for alias, canonical in SKILL_ALIASES.items():
            # Find if both alias node and canonical node exist
            result = session.run("""
                MATCH (alias:Skill)
                WHERE toLower(alias.name) = $alias_lower
                  AND alias.name <> $canonical
                RETURN alias.name AS alias_name, 
                       alias.demand_count AS demand
            """, alias_lower=alias, canonical=canonical)

            aliases_found = list(result)

            for record in aliases_found:
                alias_name = record["alias_name"]
                alias_demand = record["demand"] or 0

                # Merge: transfer all relationships to canonical node,
                # add demand counts, delete alias node
                session.run("""
                    MATCH (alias:Skill {name: $alias_name})
                    MERGE (canonical:Skill {name: $canonical})
                    ON CREATE SET canonical.demand_count = $demand,
                                  canonical.source = 'normalized'

                    // Transfer COVERS relationships
                    WITH alias, canonical
                    OPTIONAL MATCH (c:Course)-[r:COVERS]->(alias)
                    FOREACH (_ IN CASE WHEN c IS NOT NULL THEN [1] ELSE [] END |
                        MERGE (c)-[:COVERS]->(canonical)
                    )

                    // Transfer LEADS_TO relationships (outgoing)
                    WITH alias, canonical
                    OPTIONAL MATCH (alias)-[r:LEADS_TO]->(target:Skill)
                    FOREACH (_ IN CASE WHEN target IS NOT NULL THEN [1] ELSE [] END |
                        MERGE (canonical)-[:LEADS_TO]->(target)
                    )

                    // Transfer LEADS_TO relationships (incoming)
                    WITH alias, canonical
                    OPTIONAL MATCH (source:Skill)-[r:LEADS_TO]->(alias)
                    FOREACH (_ IN CASE WHEN source IS NOT NULL THEN [1] ELSE [] END |
                        MERGE (source)-[:LEADS_TO]->(canonical)
                    )

                    // Transfer REQUIRES relationships
                    WITH alias, canonical
                    OPTIONAL MATCH (j:Job)-[r:REQUIRES]->(alias)
                    FOREACH (_ IN CASE WHEN j IS NOT NULL THEN [1] ELSE [] END |
                        MERGE (j)-[:REQUIRES]->(canonical)
                    )

                    // Add demand counts and delete alias
                    WITH alias, canonical
                    SET canonical.demand_count = coalesce(canonical.demand_count, 0) 
                                               + coalesce(alias.demand_count, 0)
                    DETACH DELETE alias
                """, alias_name=alias_name, canonical=canonical, demand=alias_demand)

                print(f"  ✅ Merged '{alias_name}' → '{canonical}'")
                merged_count += 1

    print(f"\n🎉 Cleanup complete! Merged {merged_count} duplicate skill nodes.")

if __name__ == "__main__":
    cleanup_duplicate_skills()
