from app.services.graph_builder import graph_builder
from app.core.config import settings
from datetime import datetime, timezone

class AnalyticsService:

    def take_velocity_snapshot(self):
        """
        Step 1 of velocity: saves current demand_count as a snapshot.
        Called by Celery watchdog on every run before calculating velocity.
        """
        now = datetime.now(timezone.utc).isoformat()
        with graph_builder.driver.session() as session:
            session.run("""
                MATCH (s:Skill)
                WHERE s.demand_count > 0
                SET s.demand_snapshot = coalesce(s.demand_snapshot, s.demand_count),
                    s.snapshot_time   = coalesce(s.snapshot_time, $now)
            """, now=now)

    def calculate_and_store_velocity(self):
        """
        Step 2 of velocity: computes % change since last snapshot,
        stores it as s.velocity on each Skill node, then refreshes snapshot.
        Returns list of high-velocity skills that breach the threshold.
        """
        threshold = settings.VELOCITY_ALERT_THRESHOLD
        now = datetime.now(timezone.utc).isoformat()

        with graph_builder.driver.session() as session:
            # Calculate velocity for all skills that have a snapshot
            result = session.run("""
                MATCH (s:Skill)
                WHERE s.demand_snapshot IS NOT NULL
                  AND s.demand_snapshot > 0
                  AND s.demand_count > s.demand_snapshot

                WITH s,
                     s.demand_count AS current,
                     s.demand_snapshot AS previous,
                     round(
                         toFloat(s.demand_count - s.demand_snapshot)
                         / s.demand_snapshot * 100.0,
                         2
                     ) AS velocity

                SET s.velocity       = velocity,
                    s.demand_snapshot = s.demand_count,
                    s.snapshot_time   = $now

                RETURN s.name AS skill,
                       s.category AS category,
                       current,
                       previous,
                       velocity
                ORDER BY velocity DESC
            """, now=now)

            all_skills = [dict(r) for r in result]

            # Filter to only those breaching threshold
            hot_skills = [
                {
                    "skill":    s["skill"],
                    "category": s["category"],
                    "velocity": s["velocity"],
                    "demand":   s["current"],
                    "status":   "RISING 📈"
                }
                for s in all_skills
                if s["velocity"] >= threshold
            ]

        return hot_skills

    def get_velocity_leaderboard(self, limit: int = 10):
        """
        Returns top N skills ranked by stored velocity score.
        Used by the frontend Velocity Dashboard.
        """
        with graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (s:Skill)
                WHERE s.velocity IS NOT NULL AND s.velocity > 0
                RETURN s.name     AS skill,
                       s.category AS category,
                       s.velocity AS velocity,
                       s.demand_count AS demand
                ORDER BY s.velocity DESC
                LIMIT $limit
            """, limit=limit)
            return [dict(r) for r in result]

    def check_market_velocity(self):
        """
        Legacy method kept for backwards compatibility with tasks.py.
        Now delegates to real velocity calculation.
        """
        return self.calculate_and_store_velocity()

analytics_service = AnalyticsService()
