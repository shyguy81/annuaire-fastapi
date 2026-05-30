from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, field_serializer, ConfigDict
from sqlalchemy import Column, String, DateTime, JSON, func, Integer, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


# ===== Enums =====
class RelationshipType(str, Enum):
    """Type of relationship with the contact: spouse, family member, business contact, mentor, friend, or acquaintance"""
    SPOUSE = "spouse"
    FAMILY = "family"
    BUSINESS = "business"
    MENTOR = "mentor"
    FRIEND = "friend"
    ACQUAINTANCE = "acquaintance"


class ProximityLevel(str, Enum):
    """Relationship closeness level: cold (no relation), warm (initial contact), active (ongoing engagement), close (strong bond)"""
    COLD = "cold"
    WARM = "warm"
    ACTIVE = "active"
    CLOSE = "close"


class BusinessPotential(str, Enum):
    """Business opportunity potential: low, medium, or high"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InteractionType(str, Enum):
    """Type of interaction with the contact: call, email, meeting, message, or other"""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    MESSAGE = "message"
    OTHER = "other"


class ActionType(str, Enum):
    """Type of action to take: followup, relance (follow-up reminder), candidature (job application), email, call, or meeting"""
    FOLLOWUP = "followup"
    RELANCE = "relance"
    CANDIDATURE = "candidature"
    EMAIL = "email"
    CALL = "call"
    MEETING = "meeting"


class ActionStatus(str, Enum):
    """Status of the action: todo (pending), in_progress (being worked on), completed, or cancelled"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    """Priority level: low, medium, or high"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ===== Database Models =====
class ContactDB(Base):
    __tablename__ = "contacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nom = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    telephone = Column(String(20), nullable=True)
    adresse = Column(String(500), nullable=True)
    organisation = Column(String(255), nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    profiles = relationship("RelationshipProfileDB", back_populates="contact", cascade="all, delete-orphan")
    interactions = relationship("InteractionDB", back_populates="contact", cascade="all, delete-orphan")
    actions = relationship("RelationshipActionDB", back_populates="contact", cascade="all, delete-orphan")


class RelationshipProfileDB(Base):
    __tablename__ = "relationship_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(SQLEnum(RelationshipType, native_enum=False), nullable=False)
    proximity_level = Column(SQLEnum(ProximityLevel, native_enum=False), nullable=False)
    trust_level = Column(Integer, nullable=False)
    business_potential = Column(SQLEnum(BusinessPotential, native_enum=False), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    contact = relationship("ContactDB", back_populates="profiles")


class InteractionDB(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(SQLEnum(InteractionType, native_enum=False), nullable=False)
    interaction_date = Column(DateTime, nullable=False, default=func.now())
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    contact = relationship("ContactDB", back_populates="interactions")


class RelationshipActionDB(Base):
    __tablename__ = "relationship_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(SQLEnum(ActionType, native_enum=False), nullable=False)
    priority = Column(SQLEnum(Priority, native_enum=False), nullable=False)
    status = Column(SQLEnum(ActionStatus, native_enum=False), nullable=False)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    contact = relationship("ContactDB", back_populates="actions")


# ===== Pydantic Schemas =====
class ContactCreate(BaseModel):
    """Create a new contact"""
    nom: str
    email: EmailStr
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    organisation: Optional[str] = None
    tags: Optional[list[str]] = []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nom": "Jean Dupont",
                "email": "jean.dupont@example.com",
                "telephone": "+33612345678",
                "adresse": "123 Rue de Paris, 75001 Paris",
                "organisation": "Acme Corp",
                "tags": ["important", "vip"]
            }
        }
    )


class ContactUpdate(BaseModel):
    """Update an existing contact (all fields optional)"""
    nom: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    organisation: Optional[str] = None
    tags: Optional[list[str]] = None


class ContactResponse(BaseModel):
    """Contact response with all fields and timestamps"""
    id: str
    nom: str
    email: str
    telephone: Optional[str]
    adresse: Optional[str]
    organisation: Optional[str]
    tags: Optional[list[str]] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str | None:
        """Sérialiser les datetimes en ISO format avec Z pour JSON"""
        if not value:
            return None
        return value.isoformat() + 'Z'


# RelationshipProfile Schemas
class RelationshipProfileCreate(BaseModel):
    """Create a relationship profile for a contact"""
    relationship_type: RelationshipType
    proximity_level: ProximityLevel
    trust_level: int
    business_potential: BusinessPotential

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "relationship_type": "business",
                "proximity_level": "warm",
                "trust_level": 4,
                "business_potential": "high"
            }
        }
    )


class RelationshipProfileUpdate(BaseModel):
    """Update a relationship profile (all fields optional)"""
    relationship_type: Optional[RelationshipType] = None
    proximity_level: Optional[ProximityLevel] = None
    trust_level: Optional[int] = None
    business_potential: Optional[BusinessPotential] = None


class RelationshipProfileResponse(BaseModel):
    """Relationship profile response with all fields and timestamps"""
    id: str
    contact_id: str
    relationship_type: RelationshipType
    proximity_level: ProximityLevel
    trust_level: int
    business_potential: BusinessPotential
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str | None:
        if not value:
            return None
        return value.isoformat() + 'Z'


# Interaction Schemas
class InteractionCreate(BaseModel):
    """Create a new interaction with a contact"""
    interaction_type: InteractionType
    interaction_date: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "interaction_type": "email",
                "interaction_date": "2026-05-30T10:30:00",
                "notes": "Discussed project timeline and deliverables"
            }
        }
    )


class InteractionUpdate(BaseModel):
    """Update an interaction (all fields optional)"""
    interaction_type: Optional[InteractionType] = None
    interaction_date: Optional[datetime] = None
    notes: Optional[str] = None


class InteractionResponse(BaseModel):
    """Interaction response with all fields and timestamps"""
    id: str
    contact_id: str
    interaction_type: InteractionType
    interaction_date: datetime
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer('created_at', 'updated_at', 'interaction_date')
    def serialize_datetime(self, value: datetime) -> str | None:
        if not value:
            return None
        return value.isoformat() + 'Z'


# RelationshipAction Schemas
class RelationshipActionCreate(BaseModel):
    """Create a relationship action (task/reminder)"""
    action_type: ActionType
    priority: Priority
    status: ActionStatus
    due_date: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action_type": "followup",
                "priority": "high",
                "status": "todo",
                "due_date": "2026-06-15T17:00:00"
            }
        }
    )


class RelationshipActionUpdate(BaseModel):
    """Update a relationship action (all fields optional)"""
    action_type: Optional[ActionType] = None
    priority: Optional[Priority] = None
    status: Optional[ActionStatus] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RelationshipActionResponse(BaseModel):
    """Relationship action response with all fields and timestamps"""
    id: str
    contact_id: str
    action_type: ActionType
    priority: Priority
    status: ActionStatus
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer('created_at', 'updated_at', 'due_date', 'completed_at')
    def serialize_datetime(self, value: datetime) -> str | None:
        if not value:
            return None
        return value.isoformat() + 'Z'
