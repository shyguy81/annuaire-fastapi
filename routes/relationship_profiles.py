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
        """
        Create a relationship profile for a contact.
        
        A contact can have at most one relationship profile. This endpoint stores relationship metadata including:
        - Relationship type (spouse, family, business, mentor, friend, acquaintance)
        - Proximity level (cold, warm, active, close) - how close/engaged the relationship is
        - Trust level (numeric) - trust score for the contact
        - Business potential (low, medium, high) - business opportunity assessment
        
        **Parameters:**
        - contact_id: UUID of the contact (must exist)
        - profile: Relationship profile data
        
        **Responses:**
        - 201: Profile created successfully
        - 404: Contact not found
        - 409: Contact already has a relationship profile
        """
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
        """
        Retrieve the relationship profile for a contact.
        
        Each contact can have at most one relationship profile. This endpoint retrieves all relationship metadata.
        
        **Parameters:**
        - contact_id: UUID of the contact
        
        **Responses:**
        - 200: Profile found and returned
        - 404: Contact not found or has no profile
        """
        profile = db.query(RelationshipProfileDB).filter(RelationshipProfileDB.contact_id == contact_id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun profil de relation trouvé pour le contact {contact_id}"
            )
        return profile

    @app.patch("/contacts/{contact_id}/relationship-profile", response_model=RelationshipProfileResponse)
    def update_relationship_profile(contact_id: str, profile_update: RelationshipProfileUpdate, db: Session = Depends(get_db)):
        """
        Update the relationship profile for a contact.
        
        All fields are optional. Only provided fields will be updated. This allows partial updates to the profile.
        
        **Parameters:**
        - contact_id: UUID of the contact
        - profile_update: Fields to update (all optional)
        
        **Responses:**
        - 200: Profile updated successfully
        - 404: Contact not found or has no profile
        - 400: Invalid field values (e.g., invalid enum values)
        """
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
