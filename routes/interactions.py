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

    @app.post("/contacts/{contact_id}/interactions", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
    def create_interaction(contact_id: str, interaction: InteractionCreate, db: Session = Depends(get_db)):
        """Créer une nouvelle interaction pour un contact"""
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

    @app.get("/contacts/{contact_id}/interactions")
    def list_interactions(
        contact_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        type_filter: str = Query(None, alias="type"),
        since: str = Query(None),
        db: Session = Depends(get_db)
    ):
        """Lister les interactions d'un contact avec filtres et pagination"""
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
