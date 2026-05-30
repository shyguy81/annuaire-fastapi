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

    @app.post("/contacts/{contact_id}/relationship-actions", response_model=RelationshipActionResponse, status_code=status.HTTP_201_CREATED, tags=["Actions"])
    def create_relationship_action(contact_id: str, action: RelationshipActionCreate, db: Session = Depends(get_db)):
        """
        Create a new relationship action (task/reminder) for a contact.
        
        Actions represent tasks or reminders to be completed with a contact. They have status, priority, and optional due date.
        
        **Parameters:**
        - contact_id: UUID of the contact
        - action: Action data (type, priority, status, optional due_date)
        
        **Responses:**
        - 201: Action created successfully
        - 404: Contact not found
        """
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

    @app.get("/relationship-actions", tags=["Actions"])
    def list_relationship_actions(
        skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return (max 1000)"),
        status_filter: str = Query(None, alias="status", description="Filter by action status (todo, in_progress, completed, cancelled)"),
        priority_filter: str = Query(None, alias="priority", description="Filter by priority (low, medium, high)"),
        contact_id: str = Query(None, description="Filter by contact UUID"),
        db: Session = Depends(get_db)
    ):
        """
        List all relationship actions with optional filtering and pagination.
        
        Returns a paginated list of all actions. Supports filtering by status, priority, and/or contact.
        
        **Parameters:**
        - skip: Number of records to skip (default 0)
        - limit: Maximum records to return (default 100, max 1000)
        - status: Filter by status (todo, in_progress, completed, cancelled)
        - priority: Filter by priority (low, medium, high)
        - contact_id: Filter by contact UUID
        
        **Responses:**
        - 200: Actions list returned with pagination metadata
        - 400: Invalid filter values
        """
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

    @app.get("/relationship-actions/due", tags=["Actions"])
    def list_due_relationship_actions(
        skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return (max 1000)"),
        db: Session = Depends(get_db)
    ):
        """
        List actions that are due today or overdue.
        
        Returns actions with status 'todo' or 'in_progress' that have a due date on or before today.
        Includes metadata about due_today and overdue counts.
        
        **Parameters:**
        - skip: Number of records to skip (default 0)
        - limit: Maximum records to return (default 100, max 1000)
        
        **Responses:**
        - 200: List of due/overdue actions with detailed count information
        """
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

    @app.patch("/relationship-actions/{action_id}", response_model=RelationshipActionResponse, tags=["Actions"])
    def update_relationship_action(action_id: str, action_update: RelationshipActionUpdate, db: Session = Depends(get_db)):
        """
        Update a relationship action.
        
        All fields are optional. Only provided fields will be updated. Allows partial updates.
        
        **Parameters:**
        - action_id: UUID of the action to update
        - action_update: Fields to update (all optional)
        
        **Responses:**
        - 200: Action updated successfully
        - 404: Action not found
        - 400: Invalid field values
        """
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
        """
        Mark a relationship action as completed.
        
        Sets the action status to 'completed' and records the completion timestamp.
        
        **Parameters:**
        - action_id: UUID of the action to mark complete
        
        **Responses:**
        - 200: Action marked as completed
        - 404: Action not found
        """
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
