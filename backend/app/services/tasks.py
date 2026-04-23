from app.core.celery_app import celery_app
from app.services.analytics import analytics_service
from app.services.graph_builder import graph_builder
from celery.utils.log import get_task_logger
from datetime import datetime, timezone

logger = get_task_logger(__name__)

@celery_app.task(name="analyze_trends")
def analyze_trends_task():
    """
    The Proactive Watchdog — runs every 10 seconds.
    
    Cycle:
      1. Take a demand snapshot (first run seeds the baseline)
      2. Calculate velocity (% change since last snapshot)
      3. If any skill breaches the threshold → trigger automated audit
      4. Store AuditEvent node in Neo4j for frontend to poll
    """
    logger.info("🔍 Watchdog: Analyzing market velocity...")

    # Step 1: Seed snapshots for any skills that don't have one yet
    analytics_service.take_velocity_snapshot()

    # Step 2: Calculate velocity and get hot skills
    hot_skills = analytics_service.calculate_and_store_velocity()

    if not hot_skills:
        logger.info("✅ Market stable. No velocity threshold breaches.")
        return {"status": "stable"}

    # Step 3: Threshold breached — log alert
    logger.warning(f"🚨 ALERT: {len(hot_skills)} high-velocity skill(s) detected: "
                   f"{[s['skill'] for s in hot_skills]}")

    # Step 4: Store AuditEvent in Neo4j so frontend can poll it
    _store_audit_event(hot_skills)

    # Step 5: Trigger the gap analyzer automatically
    _trigger_automated_audit(hot_skills)

    return {
        "status": "alert_triggered",
        "count":  len(hot_skills),
        "skills": hot_skills
    }


def _store_audit_event(hot_skills: list):
    """Persists an AuditEvent node in Neo4j with timestamp and triggered skills."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        skill_names = [s["skill"] for s in hot_skills]
        top_velocity = hot_skills[0]["velocity"] if hot_skills else 0

        with graph_builder.driver.session() as session:
            session.run("""
                CREATE (e:AuditEvent {
                    triggered_at:   $now,
                    trigger_reason: 'velocity_threshold_breach',
                    skills_count:   $count,
                    top_skill:      $top_skill,
                    top_velocity:   $top_velocity,
                    skill_names:    $skill_names
                })
            """,
            now=now,
            count=len(hot_skills),
            top_skill=hot_skills[0]["skill"],
            top_velocity=top_velocity,
            skill_names=skill_names
            )
        logger.info(f"📝 AuditEvent stored in Neo4j at {now}")
    except Exception as e:
        logger.error(f"❌ Failed to store AuditEvent: {e}")


def _trigger_automated_audit(hot_skills: list):
    """
    Runs the gap analyzer for each high-velocity skill
    and logs actionable recommendations.
    This is the 'proactive governance' loop completing end-to-end.
    """
    try:
        from app.services.gap_analyzer import gap_analyzer

        logger.info("🤖 Triggering automated Gap Analysis...")

        for skill_data in hot_skills[:3]:  # Top 3 to avoid overload
            skill_name = skill_data["skill"]
            recommendations = gap_analyzer.get_insertion_recommendations(skill_name)

            if recommendations:
                logger.warning(
                    f"📋 AUTO-RECOMMENDATION for '{skill_name}' "
                    f"(velocity: {skill_data['velocity']}%): "
                    f"Insert into → {[r['recommended_course'] for r in recommendations]}"
                )
            else:
                logger.info(f"ℹ️ No course match found for '{skill_name}' — "
                            f"may need a new course.")

        logger.info("✅ Automated audit cycle complete.")

    except Exception as e:
        logger.error(f"❌ Automated audit failed: {e}")
