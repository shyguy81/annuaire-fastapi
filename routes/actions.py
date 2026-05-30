"""
Routes for RelationshipAction endpoints
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date
from database import get_db
from models import ContactDB, RelationshipActionDB, RelationshipActionCreate, RelationshipActionUpdate, RelationshipActionResponse, ActionStatus, Priority
import logging

logger = logging.getLogger(__name__)


def register_action_routes(app: FastAPI):
    """Register all relationship action endpoints"""

    @app.post("/contacts/{contact_id}/relationship-actions", response_model=RelationshipActionResponse, status_code=status.HTTP_201_CREATED)
    def create_relationship_action(contact_id: str, action: RelationshipActionCreate, db: Session = Depends(get_db)):
        """Créer une nouvelle action de suivi pour un contact"""
        # Vérifier que le contact existe
        contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact {contact_id} non trouvé"
            )

        db_action = RelationshipActionDB(
            contact_id=contact_id,
            **action.model_dump()
        )
        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        logger.info(f"Action de suivi créée: {db_action.id} pour contact {contact_id}")
        return db_action

    @app.get("/relationship-actions")
    def list_relationship_actions(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        status_filter: str = Query(None, alias="status"),
        priority_filter: str = Query(None, alias="priority"),
        contact_id: str = Query(None),
        db: Session = Depends(get_db)
    ):
        """Lister toutes les actions de suivi avec filtres et pagination"""
        query = db.query(RelationshipActionDB)

        # Filtrer par statut si fourni
        if status_filter:
            try:
                action_status = ActionStatus(status_filter)
                query = query.filter(RelationshipActionDB.status == action_status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status_filter}. Valid values: {', '.join([e.value for e in ActionStatus])}"
                )

        # Filtrer par priorité si fourni
        if priority_filter:
            try:
                priority = Priority(priority_filter)
                query = query.filter(RelationshipActionDB.priority == priority)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid priority: {priority_filter}. Valid values: {', '.join([e.value for e in Priority])}"
                )

        # Filtrer par contact_id si fourni
        if contact_id:
            query = query.filter(RelationshipActionDB.contact_id == contact_id)

        # Obtenir le total avant pagination
        total = query.count()

        # Appliquer pagination
        actions = query.offset(skip).limit(limit).all()

        return {
            "items": [RelationshipActionResponse.model_validate(a) for a in actions],
            "total": total,
            "skip": skip,
            "limit": limit
        }

    @app.get("/relationship-actions/due")
    def list_due_relationship_actions(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db)
    ):
        """Lister les actions dues aujourd'hui et en retard"""
        today = date.today()

        # Query for actions due today or overdue AND not completed/cancelled
        query = db.query(RelationshipActionDB).filter(
            and_(
                RelationshipActionDB.due_date <= today,
                RelationshipActionDB.status.in_([ActionStatus.TODO, ActionStatus.IN_PROGRESS])
            )
        )

        # Count overdue (due < today)
        overdue_count = db.query(RelationshipActionDB).filter(
            and_(
                RelationshipActionDB.due_date < today,
                RelationshipActionDB.status.in_([ActionStatus.TODO, ActionStatus.IN_PROGRESS])
            )
        ).count()

        # Count due today
        due_today_count = db.query(RelationshipActionDB).filter(
            and_(
                RelationshipActionDB.due_date == today,
                RelationshipActionDB.status.in_([ActionStatus.TODO, ActionStatus.IN_PROGRESS])
            )
        ).count()

        # Get total
        total = query.count()

        # Apply pagination
        actions = query.offset(skip).limit(limit).all()

        return {
            "items": [RelationshipActionResponse.model_validate(a) for a in actions],
            "total": total,
            "due_today": due_today_count,
            "overdue": overdue_count,
            "skip": skip,
            "limit": limit
        }

    @app.patch("/relationship-actions/{action_id}", response_model=RelationshipActionResponse)
    def update_relationship_action(action_id: str, action_update: RelationshipActionUpdate, db: Session = Depends(get_db)):
        """Mettre à jour une action de suivi"""
        db_action = db.query(RelationshipActionDB).filter(RelationshipActionDB.id == action_id).first()
        if not db_action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action {action_id} non trouvée"
            )

        update_data = action_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_action, field, value)

        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        logger.info(f"Action mise à jour: {action_id}")
        return db_action

    @app.patch("/relationship-actions/{action_id}/complete", response_model=RelationshipActionResponse)
    def complete_relationship_action(action_id: str, db: Session = Depends(get_db)):
        """Marquer une action comme terminée"""
        db_action = db.query(RelationshipActionDB).filter(RelationshipActionDB.id == action_id).first()
        if not db_action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action {action_id} non trouvée"
            )

        db_action.status = ActionStatus.COMPLETED
        db_action.completed_at = datetime.now()

        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        logger.info(f"Action terminée: {action_id}")
        return db_action
