"""
Routes for RelationshipProfile endpoints
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import ContactDB, RelationshipProfileDB, RelationshipProfileCreate, RelationshipProfileUpdate, RelationshipProfileResponse
import logging

logger = logging.getLogger(__name__)


def register_relationship_profile_routes(app: FastAPI):
    """Register all relationship profile endpoints"""

    @app.post("/contacts/{contact_id}/relationship-profile", response_model=RelationshipProfileResponse, status_code=status.HTTP_201_CREATED)
    def create_relationship_profile(contact_id: str, profile: RelationshipProfileCreate, db: Session = Depends(get_db)):
        """Créer un profil de relation pour un contact"""
        # Vérifier que le contact existe
        contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact {contact_id} non trouvé"
            )

        # Vérifier que le contact n'a pas déjà un profil
        existing = db.query(RelationshipProfileDB).filter(RelationshipProfileDB.contact_id == contact_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Le contact {contact_id} a déjà un profil de relation"
            )

        db_profile = RelationshipProfileDB(
            contact_id=contact_id,
            **profile.model_dump()
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        logger.info(f"Profil de relation créé: {db_profile.id} pour contact {contact_id}")
        return db_profile

    @app.get("/contacts/{contact_id}/relationship-profile", response_model=RelationshipProfileResponse)
    def get_relationship_profile(contact_id: str, db: Session = Depends(get_db)):
        """Récupérer le profil de relation d'un contact"""
        profile = db.query(RelationshipProfileDB).filter(RelationshipProfileDB.contact_id == contact_id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun profil de relation trouvé pour le contact {contact_id}"
            )
        return profile

    @app.patch("/contacts/{contact_id}/relationship-profile", response_model=RelationshipProfileResponse)
    def update_relationship_profile(contact_id: str, profile_update: RelationshipProfileUpdate, db: Session = Depends(get_db)):
        """Mettre à jour le profil de relation d'un contact"""
        db_profile = db.query(RelationshipProfileDB).filter(RelationshipProfileDB.contact_id == contact_id).first()
        if not db_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun profil de relation trouvé pour le contact {contact_id}"
            )

        # Validate trust_level if provided
        update_data = profile_update.model_dump(exclude_unset=True)
        if "trust_level" in update_data and update_data["trust_level"] is not None:
            if not 1 <= update_data["trust_level"] <= 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="trust_level doit être entre 1 et 5"
                )

        for field, value in update_data.items():
            if value is not None:
                setattr(db_profile, field, value)

        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        logger.info(f"Profil de relation mis à jour: {db_profile.id}")
        return db_profile
