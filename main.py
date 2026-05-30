from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date
from database import init_db, get_db
from models import (
    ContactDB, ContactCreate, ContactUpdate, ContactResponse,
    RelationshipProfileDB, RelationshipProfileCreate, RelationshipProfileUpdate, RelationshipProfileResponse,
    InteractionDB, InteractionCreate, InteractionResponse, InteractionType,
    RelationshipActionDB, RelationshipActionCreate, RelationshipActionUpdate, RelationshipActionResponse,
    ActionStatus, ActionType, Priority
)
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


# ===== RELATIONSHIP PROFILE ENDPOINTS =====

@app.post("/contacts/{contact_id}/relationship-profile", response_model=RelationshipProfileResponse, status_code=status.HTTP_201_CREATED)
def create_relationship_profile(contact_id: str, profile: RelationshipProfileCreate, db: Session = Depends(get_db)):
    """Créer un profil relationnel pour un contact"""
    # Vérifier que le contact existe
    contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} non trouvé"
        )
    
    # Vérifier qu'un seul profil par contact
    existing_profile = db.query(RelationshipProfileDB).filter(
        RelationshipProfileDB.contact_id == contact_id
    ).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contact {contact_id} a déjà un profil relationnel"
        )
    
    # Valider trust_level
    if profile.trust_level < 1 or profile.trust_level > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="trust_level doit être entre 1 et 5"
        )
    
    db_profile = RelationshipProfileDB(
        contact_id=contact_id,
        **profile.model_dump()
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    logger.info(f"Profil relationnel créé: {db_profile.id} pour contact {contact_id}")
    return db_profile


@app.get("/contacts/{contact_id}/relationship-profile", response_model=RelationshipProfileResponse)
def get_relationship_profile(contact_id: str, db: Session = Depends(get_db)):
    """Récupérer le profil relationnel d'un contact"""
    profile = db.query(RelationshipProfileDB).filter(
        RelationshipProfileDB.contact_id == contact_id
    ).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil relationnel non trouvé pour contact {contact_id}"
        )
    return profile


@app.patch("/contacts/{contact_id}/relationship-profile", response_model=RelationshipProfileResponse)
def update_relationship_profile(contact_id: str, profile_update: RelationshipProfileUpdate, db: Session = Depends(get_db)):
    """Mettre à jour le profil relationnel d'un contact"""
    db_profile = db.query(RelationshipProfileDB).filter(
        RelationshipProfileDB.contact_id == contact_id
    ).first()
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil relationnel non trouvé pour contact {contact_id}"
        )
    
    # Valider trust_level si fourni
    update_data = profile_update.model_dump(exclude_unset=True)
    if 'trust_level' in update_data and update_data['trust_level'] is not None:
       if update_data['trust_level'] < 1 or update_data['trust_level'] > 5:
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
    logger.info(f"Profil relationnel mis à jour: {db_profile.id} pour contact {contact_id}")
    return db_profile


# ===== INTERACTION ENDPOINTS =====

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


class InteractionsListResponse(InteractionResponse.__class__):
    """Response with pagination metadata"""
    pass


@app.get("/contacts/{contact_id}/interactions")
def list_interactions(
    contact_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: str = Query(None),
    since: str = Query(None),
    db: Session = Depends(get_db)
):
    """Lister les interactions d'un contact avec pagination et filtres"""
    # Vérifier que le contact existe
    contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact {contact_id} non trouvé"
        )
    
    # Construire la requête
    query = db.query(InteractionDB).filter(InteractionDB.contact_id == contact_id)
    
    # Filtrer par type si fourni
    if type:
        try:
            interaction_type = InteractionType(type)
            query = query.filter(InteractionDB.interaction_type == interaction_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid interaction type: {type}. Valid values: {', '.join([e.value for e in InteractionType])}"
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


# ===== RELATIONSHIP ACTION ENDPOINTS =====

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
