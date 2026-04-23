from neo4j import GraphDatabase
from app.core.config import settings
from app.services.skill_normalizer import normalize, normalize_list

class GraphBuilderService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def build_syllabus_graph(self, graph_data: dict):
        """
        Builds the academic structure from the Syllabus JSON.
        Normalizes all skill names before MERGE to prevent duplicates.
        """
        course_title = graph_data.get("course_title", "Unknown Course")
        raw_concepts = graph_data.get("concepts", [])

        # Normalize all concept names and prerequisites
        concepts = []
        for c in raw_concepts:
            concepts.append({
                "concept_name":  normalize(c["concept_name"]),
                "category":      c.get("category", ""),
                "prerequisites": normalize_list(c.get("prerequisites", []))
            })

        with self.driver.session() as session:
            session.run("MERGE (c:Course {name: $name})", name=course_title)

            session.run("""
                UNWIND $concepts AS concept
                MATCH (c:Course {name: $course_name})
                MERGE (k:Skill {name: concept.concept_name})
                SET k.category = concept.category
                MERGE (c)-[:COVERS]->(k)

                FOREACH (prereq IN concept.prerequisites |
                    MERGE (p:Skill {name: prereq})
                    MERGE (p)-[:LEADS_TO]->(k)
                )
            """, course_name=course_title, concepts=concepts)

        return {"status": "success", "nodes_created": len(concepts)}

    def process_job_batch(self, jobs_list: list):
        """
        Batch processes job market data.
        Normalizes all skill names before MERGE.
        """
        # Normalize skills in every job
        normalized_jobs = []
        for job in jobs_list:
            normalized_jobs.append({
                "job_id": job["job_id"],
                "title":  job["title"],
                "skills": normalize_list(job.get("skills", []))
            })

        with self.driver.session() as session:
            session.run("""
                UNWIND $batch AS job

                MERGE (j:Job {id: job.job_id})
                SET j.title = job.title

                FOREACH (skill_name IN job.skills |
                    MERGE (s:Skill {name: skill_name})
                    ON CREATE SET s.demand_count = 1,
                                  s.source       = 'Market_Gap'
                    ON MATCH  SET s.demand_count = coalesce(s.demand_count, 0) + 1
                    MERGE (j)-[:REQUIRES]->(s)
                )
            """, batch=normalized_jobs)

        return {"status": "batch_processed", "count": len(normalized_jobs)}

graph_builder = GraphBuilderService()
