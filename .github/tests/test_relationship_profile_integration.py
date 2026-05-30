"""
Integration tests for Relationship Profile API

These tests are designed to run against a real PostgreSQL database.
To run: 
  docker compose up
  python -m pytest test_relationship_profile_integration.py -v

Note: Unit tests are included in test_models.py for model validation.
"""

import pytest
import requests
import time
import uuid
from models import RelationshipType, ProximityLevel, BusinessPotential

BASE_URL = "http://localhost:8000"
MAX_RETRIES = 10
RETRY_DELAY = 1


@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    """Wait for API to be ready"""
    for i in range(MAX_RETRIES):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            if i < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError("API did not become ready in time")


@pytest.fixture
def create_test_contact():
    """Factory to create test contacts"""
    contact_ids = []
    
    def _create(nom="Test", email="test@example.com", **kwargs):
        unique_email = f"{uuid.uuid4().hex[:8]}_" + email
        response = requests.post(
            f"{BASE_URL}/contacts",
            json={
                "nom": nom,
                "email": unique_email,
                **kwargs
            }
        )
        assert response.status_code == 201
        contact = response.json()
        contact_ids.append(contact["id"])
        return contact
    
    yield _create
    
    # Cleanup
    for contact_id in contact_ids:
        try:
            requests.delete(f"{BASE_URL}/contacts/{contact_id}")
        except:
            pass


def test_post_relationship_profile_success(create_test_contact):
    """Test creating a relationship profile successfully"""
    contact = create_test_contact()
    
    response = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={
            "relationship_type": "business",
            "proximity_level": "warm",
            "trust_level": 4,
            "business_potential": "high"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["contact_id"] == contact["id"]
    assert data["relationship_type"] == "business"
    assert data["proximity_level"] == "warm"
    assert data["trust_level"] == 4
    assert data["business_potential"] == "high"


def test_post_relationship_profile_contact_not_found():
    """Test POST with non-existent contact"""
    response = requests.post(
        f"{BASE_URL}/contacts/invalid-id/relationship-profile",
        json={
            "relationship_type": "business",
            "proximity_level": "warm",
            "trust_level": 3,
            "business_potential": "medium"
        }
    )
    assert response.status_code == 404


def test_post_relationship_profile_duplicate(create_test_contact):
    """Test POST duplicate profile returns 409 Conflict"""
    contact = create_test_contact()
    
    # Create first profile
    response1 = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={
            "relationship_type": "business",
            "proximity_level": "warm",
            "trust_level": 3,
            "business_potential": "medium"
        }
    )
    assert response1.status_code == 201
    
    # Try to create duplicate
    response2 = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={
            "relationship_type": "friend",
            "proximity_level": "active",
            "trust_level": 3,
            "business_potential": "low"
        }
    )
    assert response2.status_code == 409


def test_post_relationship_profile_invalid_trust_level(create_test_contact):
    """Test trust_level validation (type validation)"""
    contact = create_test_contact()
    
    # Test trust_level with invalid type (string instead of int)
    response = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={
            "relationship_type": "business",
            "proximity_level": "warm",
            "trust_level": "invalid",
            "business_potential": "high"
        }
    )
    # Should return 422 for type validation error
    assert response.status_code == 422


def test_get_relationship_profile_success(create_test_contact):
    """Test GET relationship profile successfully"""
    contact = create_test_contact()
    
    # Create profile
    post_response = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={
            "relationship_type": "business",
            "proximity_level": "warm",
            "trust_level": 4,
            "business_potential": "high"
        }
    )
    assert post_response.status_code == 201
    
    # Get profile
    get_response = requests.get(f"{BASE_URL}/contacts/{contact['id']}/relationship-profile")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["relationship_type"] == "business"


def test_get_relationship_profile_not_found(create_test_contact):
    """Test GET returns 404 if profile doesn't exist"""
    contact = create_test_contact()
    response = requests.get(f"{BASE_URL}/contacts/{contact['id']}/relationship-profile")
    assert response.status_code == 404


def test_patch_relationship_profile_success(create_test_contact):
    """Test PATCH updates relationship profile"""
    contact = create_test_contact()
    
    # Create profile
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={
            "relationship_type": "business",
            "proximity_level": "warm",
            "trust_level": 4,
            "business_potential": "high"
        }
    )
    
    # Update profile
    patch_response = requests.patch(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={
            "proximity_level": "close",
            "trust_level": 5
        }
    )
    assert patch_response.status_code == 200
    data = patch_response.json()
    assert data["proximity_level"] == "close"
    assert data["trust_level"] == 5
    # Unchanged fields
    assert data["relationship_type"] == "business"


def test_patch_relationship_profile_not_found(create_test_contact):
    """Test PATCH returns 404 if profile doesn't exist"""
    contact = create_test_contact()
    response = requests.patch(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={"trust_level": 3}
    )
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
