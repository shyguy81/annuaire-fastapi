"""
Routes for Contact endpoints (CRUD + search)
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import ContactDB, ContactCreate, ContactUpdate, ContactResponse
import logging

logger = logging.getLogger(__name__)


def register_contact_routes(app: FastAPI):
    """Register all contact-related endpoints"""

    @app.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, tags=["Contacts"])
    def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
        """Créer un nouveau contact"""
        # Vérifier email unique
        existing = db.query(ContactDB).filter(ContactDB.email == contact.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {contact.email} déjà utilisé"
            )

        db_contact = ContactDB(**contact.model_dump())
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        logger.info(f"Contact créé: {db_contact.id}")
        return db_contact

    @app.get("/contacts", response_model=list[ContactResponse], tags=["Contacts"])
    def list_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        """Lister tous les contacts"""
        return db.query(ContactDB).offset(skip).limit(limit).all()

    @app.get("/contacts/{contact_id}", response_model=ContactResponse, tags=["Contacts"])
    def get_contact(contact_id: str, db: Session = Depends(get_db)):
        """Récupérer un contact par ID"""
        contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact {contact_id} non trouvé"
            )
        return contact

    @app.put("/contacts/{contact_id}", response_model=ContactResponse, tags=["Contacts"])
    def update_contact(contact_id: str, contact_update: ContactUpdate, db: Session = Depends(get_db)):
        """Mettre à jour un contact"""
        db_contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not db_contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact {contact_id} non trouvé"
            )

        # Check if new email is unique (if provided and different)
        if contact_update.email and contact_update.email != db_contact.email:
            existing = db.query(ContactDB).filter(ContactDB.email == contact_update.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {contact_update.email} déjà utilisé"
                )

        update_data = contact_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_contact, field, value)

        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        logger.info(f"Contact mis à jour: {contact_id}")
        return db_contact

    @app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Contacts"])
    def delete_contact(contact_id: str, db: Session = Depends(get_db)):
        """Supprimer un contact"""
        db_contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not db_contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact {contact_id} non trouvé"
            )

        db.delete(db_contact)
        db.commit()
        logger.info(f"Contact supprimé: {contact_id}")

    @app.get("/contacts/search/{query}", response_model=list[ContactResponse], tags=["Contacts"])
    def search_contacts(query: str, db: Session = Depends(get_db)):
        """Rechercher des contacts par nom ou email"""
        return db.query(ContactDB).filter(
            (ContactDB.nom.ilike(f"%{query}%")) |
            (ContactDB.email.ilike(f"%{query}%"))
        ).all()
