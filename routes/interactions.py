"""
Routes for Interaction endpoints
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from database import get_db
from models import ContactDB, InteractionDB, InteractionCreate, InteractionResponse, InteractionType
import logging

logger = logging.getLogger(__name__)


def register_interaction_routes(app: FastAPI):
    """Register all interaction endpoints"""

    @app.post("/contacts/{contact_id}/interactions", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED, tags=["Interactions"])
    def create_interaction(contact_id: str, interaction: InteractionCreate, db: Session = Depends(get_db)):
        """
        Create a new interaction record for a contact.
        
        Records an interaction (call, email, meeting, message, or other) with a contact. Useful for tracking communication history.
        
        **Parameters:**
        - contact_id: UUID of the contact
        - interaction: Interaction data (type is required, date defaults to now if not provided)
        
        **Responses:**
        - 201: Interaction created successfully
        - 404: Contact not found
        """
        # Vérifier que le contact existe
        contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact {contact_id} non trouvé"
            )

        db_interaction = InteractionDB(
            contact_id=contact_id,
            **interaction.model_dump()
        )
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)
        logger.info(f"Interaction créée: {db_interaction.id} pour contact {contact_id}")
        return db_interaction

    @app.get("/contacts/{contact_id}/interactions", tags=["Interactions"])
    def list_interactions(
        contact_id: str,
        skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return (max 1000)"),
        type_filter: str = Query(None, alias="type", description="Filter by interaction type (call, email, meeting, message, other)"),
        since: str = Query(None, description="Filter interactions on or after this date (YYYY-MM-DD)"),
        db: Session = Depends(get_db)
    ):
        """
        List all interactions for a contact with optional filtering and pagination.
        
        Returns a paginated list of interaction records. Supports filtering by interaction type and date range.
        
        **Parameters:**
        - contact_id: UUID of the contact
        - skip: Number of records to skip (default 0)
        - limit: Maximum records to return (default 100, max 1000)
        - type: Filter by interaction type (call, email, meeting, message, other)
        - since: Filter interactions on or after date (format: YYYY-MM-DD)
        
        **Responses:**
        - 200: Interactions list returned with pagination metadata
        - 404: Contact not found
        - 400: Invalid filter values
        """
        # Vérifier que le contact existe
        contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact {contact_id} non trouvé"
            )

        query = db.query(InteractionDB).filter(InteractionDB.contact_id == contact_id)

        # Filtrer par type si fourni
        if type_filter:
            try:
                interaction_type = InteractionType(type_filter)
                query = query.filter(InteractionDB.interaction_type == interaction_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid type: {type_filter}. Valid values: {', '.join([e.value for e in InteractionType])}"
                )

        # Filtrer par date si fourni
        if since:
            try:
                since_date = datetime.fromisoformat(since).replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(InteractionDB.interaction_date >= since_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format for 'since'. Use YYYY-MM-DD"
                )

        # Obtenir le total avant pagination
        total = query.count()

        # Appliquer pagination
        interactions = query.offset(skip).limit(limit).all()

        return {
            "items": [InteractionResponse.model_validate(i) for i in interactions],
            "total": total,
            "skip": skip,
            "limit": limit
        }
