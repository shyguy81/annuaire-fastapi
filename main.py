from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import init_db, get_db
from models import ContactDB, ContactCreate, ContactUpdate, ContactResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Annuaire Contacts API", version="0.1.0")


@app.on_event("startup")
def startup():
    """Initialize database on startup"""
    init_db()
    logger.info("Database initialized")


# ===== ENDPOINTS =====

@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok"}


@app.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
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


@app.get("/contacts", response_model=list[ContactResponse])
def list_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lister tous les contacts"""
    contacts = db.query(ContactDB).offset(skip).limit(limit).all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: str, db: Session = Depends(get_db)):
    """Récupérer un contact par ID"""
    contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} non trouvé"
        )
    return contact


@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: str, contact_update: ContactUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un contact"""
    db_contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} non trouvé"
        )

    # Vérifier nouvel email unique si changé
    if contact_update.email and contact_update.email != db_contact.email:
        existing = db.query(ContactDB).filter(ContactDB.email == contact_update.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {contact_update.email} déjà utilisé"
            )

    update_data = contact_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact, field, value)

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    logger.info(f"Contact mis à jour: {db_contact.id}")
    return db_contact


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    return None


@app.get("/contacts/search/{query}", response_model=list[ContactResponse])
def search_contacts(query: str, db: Session = Depends(get_db)):
    """Chercher contacts par nom/email/organisation"""
    results = db.query(ContactDB).filter(
        (ContactDB.nom.ilike(f"%{query}%")) |
        (ContactDB.email.ilike(f"%{query}%")) |
        (ContactDB.organisation.ilike(f"%{query}%"))
    ).all()
    return results
