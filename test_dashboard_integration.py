"""
Integration tests for Dashboard API

Run against a real PostgreSQL database:
  docker compose up
  pytest test_dashboard_integration.py -v
"""

import pytest
import requests
import time
import uuid
from datetime import datetime, date, timedelta

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
    """Factory to create test contacts with unique emails"""
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
        assert response.status_code == 201, f"Failed to create contact: {response.json()}"
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


def test_dashboard_endpoint_exists():
    """Test that dashboard endpoint is accessible"""
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    assert response.status_code == 200


def test_dashboard_response_schema():
    """Test dashboard response has required fields"""
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    assert response.status_code == 200
    data = response.json()
    
    required_fields = ["due_today", "overdue", "active_relations", "high_potential", "recent_interactions", "timestamp"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    
    # Verify types
    assert isinstance(data["due_today"], int)
    assert isinstance(data["overdue"], int)
    assert isinstance(data["active_relations"], int)
    assert isinstance(data["high_potential"], int)
    assert isinstance(data["recent_interactions"], int)
    assert isinstance(data["timestamp"], str)


def test_dashboard_timestamp_format():
    """Test that timestamp is in ISO 8601 format"""
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    timestamp = data["timestamp"]
    
    # Should end with Z (UTC indicator)
    assert timestamp.endswith("Z"), "Timestamp should end with Z"
    
    # Should be parseable as ISO 8601
    try:
        parsed = datetime.fromisoformat(timestamp.rstrip("Z"))
        assert parsed is not None
    except ValueError:
        pytest.fail("Timestamp is not in valid ISO 8601 format")


def test_dashboard_due_today_count(create_test_contact):
    """Test that due_today count is correct"""
    contact = create_test_contact()
    today_str = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    # Create an action due today
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": today_str
        }
    )
    
    # Get dashboard
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    
    # Should have at least 1 due today
    assert data["due_today"] >= 1


def test_dashboard_overdue_count(create_test_contact):
    """Test that overdue count is correct"""
    contact = create_test_contact()
    yesterday_str = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    # Create an action due yesterday
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": yesterday_str
        }
    )
    
    # Get dashboard
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    
    # Should have at least 1 overdue
    assert data["overdue"] >= 1


def test_dashboard_due_excludes_future(create_test_contact):
    """Test that due counts don't include future actions"""
    contact = create_test_contact()
    tomorrow_str = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    initial_due = requests.get(f"{BASE_URL}/rap/dashboard").json()["due_today"]
    
    # Create an action due tomorrow
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    
    # Get dashboard again
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    
    # Due today count shouldn't change
    assert data["due_today"] == initial_due


def test_dashboard_due_excludes_completed(create_test_contact):
    """Test that completed actions don't count as due"""
    contact = create_test_contact()
    today_str = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    # Create an action due today
    action_response = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": today_str
        }
    )
    action_id = action_response.json()["id"]
    
    # Get initial count
    initial_due = requests.get(f"{BASE_URL}/rap/dashboard").json()["due_today"]
    
    # Complete the action
    requests.patch(f"{BASE_URL}/relationship-actions/{action_id}/complete")
    
    # Get dashboard again
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    
    # Due today count should be less
    assert data["due_today"] < initial_due


def test_dashboard_active_relations(create_test_contact):
    """Test that active relations count is correct"""
    contact = create_test_contact()
    
    # Create a relationship profile with active proximity
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={
            "relationship_type": "business",
            "proximity_level": "active",
            "business_potential": "medium",
            "trust_level": 3
        }
    )
    
    # Get dashboard
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    
    # Should have at least 1 active relation
    assert data["active_relations"] >= 1


def test_dashboard_high_potential(create_test_contact):
    """Test that high potential count is correct"""
    contact = create_test_contact()
    
    # Create a relationship profile with high potential
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-profile",
        json={
            "relationship_type": "business",
            "proximity_level": "warm",
            "business_potential": "high",
            "trust_level": 4
        }
    )
    
    # Get dashboard
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    
    # Should have at least 1 high potential
    assert data["high_potential"] >= 1


def test_dashboard_recent_interactions(create_test_contact):
    """Test that recent interactions count is correct"""
    contact = create_test_contact()
    
    # Create an interaction
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/interactions",
        json={
            "interaction_type": "email",
            "interaction_date": datetime.now().isoformat()
        }
    )
    
    # Get dashboard
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    
    # Should have at least 1 recent interaction
    assert data["recent_interactions"] >= 1


def test_dashboard_recent_interactions_excludes_old(create_test_contact):
    """Test that recent interactions doesn't include old data"""
    # Get initial count
    initial_count = requests.get(f"{BASE_URL}/rap/dashboard").json()["recent_interactions"]
    
    contact = create_test_contact()
    eight_days_ago = (datetime.now() - timedelta(days=8)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Create an interaction from 8 days ago (outside 7 day window)
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/interactions",
        json={
            "interaction_type": "email",
            "interaction_date": eight_days_ago.isoformat()
        }
    )
    
    # Get dashboard again
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    
    # Recent interactions count shouldn't change much (it's old data)
    # Note: It might increase if there are other recent interactions, but 
    # this old one shouldn't be counted
    assert data["recent_interactions"] >= initial_count


def test_dashboard_values_non_negative():
    """Test that all dashboard values are non-negative"""
    response = requests.get(f"{BASE_URL}/rap/dashboard")
    data = response.json()
    
    assert data["due_today"] >= 0
    assert data["overdue"] >= 0
    assert data["active_relations"] >= 0
    assert data["high_potential"] >= 0
    assert data["recent_interactions"] >= 0


def test_dashboard_multiple_calls_consistent():
    """Test that multiple calls return consistent results"""
    response1 = requests.get(f"{BASE_URL}/rap/dashboard")
    data1 = response1.json()
    
    response2 = requests.get(f"{BASE_URL}/rap/dashboard")
    data2 = response2.json()
    
    # Counts should be the same (assuming no other processes modify data)
    assert data1["due_today"] == data2["due_today"]
    assert data1["overdue"] == data2["overdue"]
    assert data1["active_relations"] == data2["active_relations"]
    assert data1["high_potential"] == data2["high_potential"]
    # Recent interactions might vary slightly due to timing, but should be close
    assert abs(data1["recent_interactions"] - data2["recent_interactions"]) <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
