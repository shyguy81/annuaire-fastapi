from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, DateTime, JSON, func
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


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


# ===== Pydantic Schemas =====
class ContactCreate(BaseModel):
    nom: str
    email: EmailStr
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    organisation: Optional[str] = None
    tags: Optional[list[str]] = []


class ContactUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    organisation: Optional[str] = None
    tags: Optional[list[str]] = None


class ContactResponse(BaseModel):
    id: str
    nom: str
    email: str
    telephone: Optional[str]
    adresse: Optional[str]
    organisation: Optional[str]
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
