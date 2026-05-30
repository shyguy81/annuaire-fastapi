import pytest
from datetime import datetime
from models import (
    ContactDB, RelationshipProfileDB, InteractionDB, RelationshipActionDB,
    RelationshipType, ProximityLevel, BusinessPotential,
    InteractionType, ActionType, ActionStatus, Priority,
    ContactCreate, ContactResponse,
    RelationshipProfileCreate, RelationshipProfileResponse,
    InteractionCreate, InteractionResponse,
    RelationshipActionCreate, RelationshipActionResponse
)


def test_contact_model_creation():
    """Test ContactDB model creation"""
    contact = ContactDB(
        nom="John Doe",
        email="john@example.com",
        telephone="+33123456789",
        organisation="TechCorp"
    )
    assert contact.nom == "John Doe"
    assert contact.email == "john@example.com"
    # ID is generated via SQLAlchemy on database insert
    assert hasattr(contact, 'id')


def test_relationship_profile_model():
    """Test RelationshipProfileDB model"""
    profile = RelationshipProfileDB(
        contact_id="test-id-123",
        relationship_type=RelationshipType.BUSINESS,
        proximity_level=ProximityLevel.WARM,
        trust_level=4,
        business_potential=BusinessPotential.HIGH
    )
    assert profile.relationship_type == RelationshipType.BUSINESS
    assert profile.proximity_level == ProximityLevel.WARM
    assert profile.trust_level == 4


def test_interaction_model():
    """Test InteractionDB model"""
    interaction = InteractionDB(
        contact_id="test-id-123",
        interaction_type=InteractionType.MEETING,
        notes="Discussed new project opportunities"
    )
    assert interaction.interaction_type == InteractionType.MEETING
    assert interaction.notes == "Discussed new project opportunities"


def test_relationship_action_model():
    """Test RelationshipActionDB model"""
    action = RelationshipActionDB(
        contact_id="test-id-123",
        action_type=ActionType.FOLLOWUP,
        priority=Priority.HIGH,
        status=ActionStatus.TODO
    )
    assert action.action_type == ActionType.FOLLOWUP
    assert action.priority == Priority.HIGH
    assert action.status == ActionStatus.TODO


def test_contact_create_schema():
    """Test ContactCreate Pydantic schema"""
    contact = ContactCreate(
        nom="Jane Doe",
        email="jane@example.com",
        telephone="+33987654321",
        organisation="StartupXYZ",
        tags=["vip", "tech"]
    )
    assert contact.nom == "Jane Doe"
    assert contact.email == "jane@example.com"
    assert contact.tags == ["vip", "tech"]


def test_relationship_profile_create_schema():
    """Test RelationshipProfileCreate Pydantic schema"""
    profile = RelationshipProfileCreate(
        relationship_type=RelationshipType.MENTOR,
        proximity_level=ProximityLevel.ACTIVE,
        trust_level=5,
        business_potential=BusinessPotential.MEDIUM
    )
    assert profile.relationship_type == RelationshipType.MENTOR
    assert profile.trust_level == 5


def test_interaction_create_schema():
    """Test InteractionCreate Pydantic schema"""
    interaction = InteractionCreate(
        interaction_type=InteractionType.EMAIL,
        notes="Email sent regarding collaboration"
    )
    assert interaction.interaction_type == InteractionType.EMAIL
    assert interaction.notes == "Email sent regarding collaboration"


def test_relationship_action_create_schema():
    """Test RelationshipActionCreate Pydantic schema"""
    action = RelationshipActionCreate(
        action_type=ActionType.RELANCE,
        priority=Priority.MEDIUM,
        status=ActionStatus.IN_PROGRESS
    )
    assert action.action_type == ActionType.RELANCE
    assert action.priority == Priority.MEDIUM
    assert action.status == ActionStatus.IN_PROGRESS


def test_enums_valid_values():
    """Test all enum values are correctly defined"""
    assert RelationshipType.BUSINESS.value == "business"
    assert RelationshipType.MENTOR.value == "mentor"
    
    assert ProximityLevel.COLD.value == "cold"
    assert ProximityLevel.CLOSE.value == "close"
    
    assert BusinessPotential.HIGH.value == "high"
    assert BusinessPotential.LOW.value == "low"
    
    assert InteractionType.CALL.value == "call"
    assert InteractionType.MEETING.value == "meeting"
    
    assert ActionType.FOLLOWUP.value == "followup"
    assert ActionType.RELANCE.value == "relance"
    
    assert ActionStatus.TODO.value == "todo"
    assert ActionStatus.COMPLETED.value == "completed"
    
    assert Priority.HIGH.value == "high"
    assert Priority.LOW.value == "low"


def test_relationship_profile_response_serialization():
    """Test RelationshipProfileResponse serialization"""
    now = datetime.now()
    response = RelationshipProfileResponse(
        id="prof-123",
        contact_id="cont-456",
        relationship_type=RelationshipType.BUSINESS,
        proximity_level=ProximityLevel.WARM,
        trust_level=4,
        business_potential=BusinessPotential.HIGH,
        created_at=now,
        updated_at=now
    )
    assert response.id == "prof-123"
    assert response.relationship_type == RelationshipType.BUSINESS


def test_interaction_response_serialization():
    """Test InteractionResponse serialization"""
    now = datetime.now()
    response = InteractionResponse(
        id="inter-789",
        contact_id="cont-456",
        interaction_type=InteractionType.MEETING,
        interaction_date=now,
        notes="Team sync meeting",
        created_at=now,
        updated_at=now
    )
    assert response.interaction_type == InteractionType.MEETING


def test_relationship_action_response_serialization():
    """Test RelationshipActionResponse serialization"""
    now = datetime.now()
    response = RelationshipActionResponse(
        id="action-101",
        contact_id="cont-456",
        action_type=ActionType.FOLLOWUP,
        priority=Priority.HIGH,
        status=ActionStatus.TODO,
        due_date=now,
        completed_at=None,
        created_at=now,
        updated_at=now
    )
    assert response.action_type == ActionType.FOLLOWUP
    assert response.status == ActionStatus.TODO
    assert response.completed_at is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
