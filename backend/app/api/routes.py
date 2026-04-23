from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingestion import ingestion_service
from app.services.llm_parser import llm_service
from app.services.graph_builder import graph_builder
from app.services.gap_analyzer import gap_analyzer
from app.services.analytics import analytics_service
from pydantic import BaseModel
from typing import List
import uuid
from app.services.report_generator import report_service

router = APIRouter()

# ── Ingestion ─────────────────────────────────────────────────────────────────

@router.post("/ingest/syllabus")
async def ingest_syllabus(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # UUID prefix to prevent filename collisions
    safe_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = await ingestion_service.save_upload(file, safe_filename)
    pdf_result = ingestion_service.extract_text_from_pdf(file_path)

    if pdf_result.get("status") == "error":
        raise HTTPException(status_code=500, detail=pdf_result.get("message"))

    structured_data = await llm_service.extract_graph_data(pdf_result["raw_text"])
    if "error" in structured_data:
        raise HTTPException(status_code=500, detail=f"AI Error: {structured_data['error']}")

    graph_status = graph_builder.build_syllabus_graph(structured_data)

    return {
        "message": "Syllabus processed & graph updated successfully",
        "filename": pdf_result["filename"],
        "graph_stats": graph_status,
        "ai_data": structured_data
    }


class JobDescription(BaseModel):
    title: str
    required_skills: List[str]

@router.post("/ingest/job")
async def ingest_job(job: JobDescription):
    job_payload = {
        "job_id": str(uuid.uuid4()),
        "title": job.title,
        "skills": job.required_skills
    }
    graph_builder.process_job_batch([job_payload])
    return {"message": "Job processed", "skills": job.required_skills}


# ── Audit & Analysis ──────────────────────────────────────────────────────────

@router.get("/audit/research_report")
async def generate_research_report(generate_text_report: bool = False):
    """Triggers Graph-RAG analysis and optionally generates a formal board report."""
    try:
        metrics  = gap_analyzer.calculate_research_metrics()
        top_gaps = gap_analyzer.get_prioritized_gaps(limit=7)

        actionable_interventions = []
        for gap in top_gaps:
            recommendations = gap_analyzer.get_insertion_recommendations(gap["missing_skill"])
            actionable_interventions.append({
                "missing_skill":    gap["missing_skill"],
                "market_demand":    gap["market_demand"],
                "suggested_courses": recommendations
            })

        audit_data = {
            "metrics": metrics,
            "actionable_interventions": actionable_interventions
        }

        ai_report = None
        if generate_text_report:
            ai_report = await report_service.generate_board_report(audit_data)

        return {
            "status":           "success",
            "raw_data":         audit_data,
            "ai_written_report": ai_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/events")
async def get_audit_events(limit: int = 10):
    """
    Returns recent AuditEvent nodes triggered by the proactive watchdog.
    Frontend polls this to show real-time alerts.
    """
    try:
        with graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (e:AuditEvent)
                RETURN e.triggered_at   AS triggered_at,
                       e.top_skill      AS top_skill,
                       e.top_velocity   AS top_velocity,
                       e.skills_count   AS skills_count,
                       e.skill_names    AS skill_names,
                       e.trigger_reason AS reason
                ORDER BY e.triggered_at DESC
                LIMIT $limit
            """, limit=limit)
            events = [dict(r) for r in result]
        return {"status": "success", "events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Velocity ──────────────────────────────────────────────────────────────────

@router.get("/analytics/velocity")
async def get_velocity_leaderboard(limit: int = 10):
    """Returns top skills ranked by current velocity score."""
    try:
        leaderboard = analytics_service.get_velocity_leaderboard(limit=limit)
        return {"status": "success", "leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Graph ─────────────────────────────────────────────────────────────────────

@router.get("/graph/visualize")
async def get_graph_visualization():
    """Fetches Courses, Skills, and their connections for the force-directed graph."""
    try:
        with graph_builder.driver.session() as session:
            result1 = session.run("""
                MATCH (c:Course)-[:COVERS]->(s:Skill)
                RETURN c.name AS source, 'Course' AS source_label,
                       s.name AS target, 'Skill'  AS target_label
                LIMIT 100
            """)
            result2 = session.run("""
                MATCH (s1:Skill)-[:LEADS_TO]->(s2:Skill)
                RETURN s1.name AS source, 'Skill' AS source_label,
                       s2.name AS target, 'Skill' AS target_label
                LIMIT 150
            """)

            nodes_dict = {}
            links = []

            for record in list(result1) + list(result2):
                src_id = record["source"]
                tgt_id = record["target"]

                if src_id not in nodes_dict:
                    nodes_dict[src_id] = {
                        "id":    src_id,
                        "group": record["source_label"],
                        "val":   25 if record["source_label"] == "Course" else 5
                    }
                if tgt_id not in nodes_dict:
                    nodes_dict[tgt_id] = {
                        "id":    tgt_id,
                        "group": record["target_label"],
                        "val":   5
                    }
                links.append({"source": src_id, "target": tgt_id})

        return {"nodes": list(nodes_dict.values()), "links": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/stats")
async def get_graph_stats():
    """Returns node counts, edge counts, top skills, and top gaps."""
    try:
        with graph_builder.driver.session() as session:
            # Eagerly collect ALL results inside the session
            node_counts = {
                r["label"]: r["count"]
                for r in session.run("""
                    MATCH (n)
                    RETURN labels(n)[0] AS label, count(n) AS count
                """)
            }
            edges = {
                r["type"]: r["count"]
                for r in session.run("""
                    MATCH ()-[r]->()
                    RETURN type(r) AS type, count(r) AS count
                """)
            }
            top_skills = [
                dict(r) for r in session.run("""
                    MATCH (s:Skill)
                    WHERE s.demand_count > 0
                    RETURN s.name AS skill, s.demand_count AS demand
                    ORDER BY s.demand_count DESC LIMIT 10
                """)
            ]
            top_gaps = [
                dict(r) for r in session.run("""
                    MATCH (s:Skill)
                    WHERE NOT ()-[:COVERS]->(s) AND s.demand_count > 0
                    RETURN s.name AS skill, s.demand_count AS demand
                    ORDER BY s.demand_count DESC LIMIT 10
                """)
            ]

        return {
            "status":      "success",
            "node_counts": node_counts,
            "edge_counts": edges,
            "top_skills":  top_skills,
            "top_gaps":    top_gaps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/audit/latency_benchmark")
async def run_latency_benchmark():
    """
    Runs all major Cypher queries and returns latency measurements.
    Use this for NFR-01 and NFR-03 validation in your project report.
    """
    try:
        report = gap_analyzer.get_full_latency_report()
        return {"status": "success", "benchmark": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/graph/build_embeddings")
async def build_embeddings():
    """Builds semantic embedding index for all Skill nodes."""
    try:
        from app.services.vector_store import vector_store
        result = vector_store.build_index()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/research_report_hybrid")
async def generate_hybrid_report(generate_text_report: bool = False):
    """Same as research_report but uses hybrid graph+semantic scoring."""
    try:
        metrics  = gap_analyzer.calculate_research_metrics()
        top_gaps = gap_analyzer.get_prioritized_gaps_hybrid(limit=7)

        actionable_interventions = []
        for gap in top_gaps:
            recommendations = gap_analyzer.get_insertion_recommendations(
                gap["missing_skill"]
            )
            actionable_interventions.append({
                "missing_skill":     gap["missing_skill"],
                "market_demand":     gap["market_demand"],
                "hybrid_score":      gap.get("hybrid_score"),
                "semantic_coverage": gap.get("semantic_coverage"),
                "suggested_courses": recommendations
            })

        audit_data = {"metrics": metrics,
                      "actionable_interventions": actionable_interventions}

        ai_report = None
        if generate_text_report:
            ai_report = await report_service.generate_board_report(audit_data)

        return {"status": "success", "raw_data": audit_data,
                "ai_written_report": ai_report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
