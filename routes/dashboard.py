"""
Routes for Dashboard endpoints - RAP system metrics aggregation
"""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date, timedelta
from database import get_db
from models import (
    RelationshipActionDB, RelationshipProfileDB, InteractionDB,
    ActionStatus, ProximityLevel, BusinessPotential
)
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class DashboardResponse(BaseModel):
    """Dashboard response with RAP system metrics"""
    due_today: int
    overdue: int
    active_relations: int
    high_potential: int
    recent_interactions: int
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "due_today": 5,
                "overdue": 2,
                "active_relations": 12,
                "high_potential": 8,
                "recent_interactions": 23,
                "timestamp": "2026-05-30T16:23:25.795000Z"
            }
        }


def register_dashboard_routes(app: FastAPI):
    """Register dashboard endpoints"""

    @app.get("/rap/dashboard", response_model=DashboardResponse, tags=["Dashboard"])
    def get_dashboard(db: Session = Depends(get_db)):
        """
        Get RAP system dashboard with aggregated metrics.
        
        Returns system-wide statistics about relationship actions, profiles, and interactions.
        All metrics are calculated in real-time using optimized SQL aggregations.
        
        **Metrics returned:**
        - due_today: Count of actions with 'todo' or 'in_progress' status due today
        - overdue: Count of actions with 'todo' or 'in_progress' status due before today
        - active_relations: Count of distinct contacts with 'warm', 'active', or 'close' proximity levels
        - high_potential: Count of distinct contacts with 'high' business potential
        - recent_interactions: Count of interactions from the last 7 days
        - timestamp: Current time in ISO 8601 format (UTC)
        
        **Responses:**
        - 200: Dashboard metrics returned successfully
        """
        today = date.today()
        seven_days_ago = today - timedelta(days=7)

        # Count actions due today
        due_today_count = db.query(func.count(RelationshipActionDB.id)).filter(
            and_(
                RelationshipActionDB.due_date == today,
                RelationshipActionDB.status.in_([ActionStatus.TODO, ActionStatus.IN_PROGRESS])
            )
        ).scalar() or 0

        # Count actions overdue
        overdue_count = db.query(func.count(RelationshipActionDB.id)).filter(
            and_(
                RelationshipActionDB.due_date < today,
                RelationshipActionDB.status.in_([ActionStatus.TODO, ActionStatus.IN_PROGRESS])
            )
        ).scalar() or 0

        # Count active relationships (distinct contacts with warm/active/close profiles)
        active_relations_count = db.query(func.count(func.distinct(RelationshipProfileDB.contact_id))).filter(
            RelationshipProfileDB.proximity_level.in_([ProximityLevel.WARM, ProximityLevel.ACTIVE, ProximityLevel.CLOSE])
        ).scalar() or 0

        # Count high potential relationships (distinct contacts with high business potential)
        high_potential_count = db.query(func.count(func.distinct(RelationshipProfileDB.contact_id))).filter(
            RelationshipProfileDB.business_potential == BusinessPotential.HIGH
        ).scalar() or 0

        # Count recent interactions (last 7 days)
        recent_interactions_count = db.query(func.count(InteractionDB.id)).filter(
            InteractionDB.interaction_date > datetime.combine(seven_days_ago, datetime.min.time())
        ).scalar() or 0

        logger.info("Dashboard metrics retrieved successfully")

        return DashboardResponse(
            due_today=due_today_count,
            overdue=overdue_count,
            active_relations=active_relations_count,
            high_potential=high_potential_count,
            recent_interactions=recent_interactions_count,
            timestamp=datetime.now().isoformat() + "Z"
        )
