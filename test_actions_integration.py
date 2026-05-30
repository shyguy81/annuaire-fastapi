"""
Integration tests for Relationship Actions API

Run against a real PostgreSQL database:
  docker compose up
  pytest test_actions_integration.py -v
"""

import pytest
import requests
import time
import uuid
from datetime import datetime, date, timedelta

BASE_URL = "http://localhost:8000"
MAX_RETRIES = 10
RETRY_DELAY = 1


def get_datetime_str(offset_days=0):
    """Get ISO datetime string with optional day offset"""
    dt = datetime.now() + timedelta(days=offset_days)
    return dt.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


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
        # Generate unique email to avoid conflicts
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


def test_post_relationship_action_success(create_test_contact):
    """Test creating a relationship action successfully"""
    contact = create_test_contact()
    tomorrow_str = get_datetime_str(1)
    
    response = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["contact_id"] == contact["id"]
    assert data["action_type"] == "followup"
    assert data["priority"] == "high"
    assert data["status"] == "todo"


def test_post_relationship_action_all_types(create_test_contact):
    """Test all action types"""
    contact = create_test_contact()
    tomorrow_str = get_datetime_str(1)
    action_types = ["followup", "relance", "candidature", "email", "call", "meeting"]
    
    for action_type in action_types:
        response = requests.post(
            f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
            json={
                "action_type": action_type,
                "priority": "medium",
                "status": "todo",
                "due_date": tomorrow_str
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["action_type"] == action_type


def test_post_relationship_action_contact_not_found():
    """Test POST with non-existent contact"""
    tomorrow_str = get_datetime_str(1)
    response = requests.post(
        f"{BASE_URL}/contacts/invalid-id/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    assert response.status_code == 404


def test_get_all_relationship_actions_empty():
    """Test GET all actions on empty system"""
    response = requests.get(f"{BASE_URL}/relationship-actions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)


def test_get_relationship_actions_pagination():
    """Test pagination in GET /relationship-actions"""
    response = requests.get(
        f"{BASE_URL}/relationship-actions?skip=0&limit=50"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 0
    assert data["limit"] == 50


def test_get_relationship_actions_filter_by_status(create_test_contact):
    """Test filtering actions by status"""
    contact = create_test_contact()
    tomorrow_str = get_datetime_str(1)
    
    # Create an action
    create_response = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    action_id = create_response.json()["id"]
    
    # Filter by status
    response = requests.get(
        f"{BASE_URL}/relationship-actions?status=todo"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert all(item["status"] == "todo" for item in data["items"])


def test_get_relationship_actions_filter_by_priority(create_test_contact):
    """Test filtering actions by priority"""
    contact = create_test_contact()
    tomorrow_str = get_datetime_str(1)
    
    # Create an action with high priority
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    
    # Filter by priority
    response = requests.get(
        f"{BASE_URL}/relationship-actions?priority=high"
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["priority"] == "high" for item in data["items"])


def test_get_relationship_actions_filter_by_contact(create_test_contact):
    """Test filtering actions by contact_id"""
    contact = create_test_contact()
    tomorrow_str = get_datetime_str(1)
    
    # Create an action
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "medium",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    
    # Filter by contact_id
    response = requests.get(
        f"{BASE_URL}/relationship-actions?contact_id={contact['id']}"
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["contact_id"] == contact["id"] for item in data["items"])


def test_get_relationship_actions_combined_filters(create_test_contact):
    """Test combining multiple filters"""
    contact = create_test_contact()
    tomorrow_str = get_datetime_str(1)
    
    # Create actions with different priorities
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "relance",
            "priority": "low",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    
    # Filter by status AND priority AND contact
    response = requests.get(
        f"{BASE_URL}/relationship-actions?status=todo&priority=high&contact_id={contact['id']}"
    )
    assert response.status_code == 200
    data = response.json()
    assert all(
        item["status"] == "todo" and item["priority"] == "high" and item["contact_id"] == contact["id"]
        for item in data["items"]
    )


def test_get_due_actions_empty():
    """Test GET due actions on empty system"""
    response = requests.get(f"{BASE_URL}/relationship-actions/due")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "due_today" in data
    assert "overdue" in data


def test_get_due_actions_today(create_test_contact):
    """Test GET due actions includes today's actions"""
    contact = create_test_contact()
    today_str = get_datetime_str(0)
    
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
    
    # Get due actions
    response = requests.get(f"{BASE_URL}/relationship-actions/due")
    assert response.status_code == 200
    data = response.json()
    assert data["due_today"] >= 1
    assert data["total"] >= 1


def test_get_due_actions_overdue(create_test_contact):
    """Test GET due actions includes overdue actions"""
    contact = create_test_contact()
    yesterday_str = get_datetime_str(-1)
    
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
    
    # Get due actions
    response = requests.get(f"{BASE_URL}/relationship-actions/due")
    assert response.status_code == 200
    data = response.json()
    assert data["overdue"] >= 1
    assert data["total"] >= 1


def test_get_due_actions_excludes_future(create_test_contact):
    """Test GET due actions doesn't include future actions"""
    contact = create_test_contact()
    tomorrow_str = get_datetime_str(1)
    
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
    
    # Get due actions - should not include future action
    response = requests.get(f"{BASE_URL}/relationship-actions/due")
    assert response.status_code == 200
    data = response.json()
    # Ensure future actions are not in due list
    for item in data["items"]:
        item_due_date = datetime.fromisoformat(item["due_date"].replace("Z", "+00:00")).date()
        assert item_due_date <= date.today()


def test_patch_relationship_action_success(create_test_contact):
    """Test updating a relationship action"""
    contact = create_test_contact()
    tomorrow_str = get_datetime_str(1)
    
    # Create an action
    create_response = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "low",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    action_id = create_response.json()["id"]
    
    # Update the action
    response = requests.patch(
        f"{BASE_URL}/relationship-actions/{action_id}",
        json={
            "priority": "high",
            "status": "in_progress"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "high"
    assert data["status"] == "in_progress"


def test_patch_relationship_action_not_found():
    """Test PATCH returns 404 for non-existent action"""
    response = requests.patch(
        f"{BASE_URL}/relationship-actions/invalid-id",
        json={"priority": "high"}
    )
    assert response.status_code == 404


def test_complete_relationship_action_success(create_test_contact):
    """Test completing a relationship action"""
    contact = create_test_contact()
    tomorrow_str = get_datetime_str(1)
    
    # Create an action
    create_response = requests.post(
        f"{BASE_URL}/contacts/{contact['id']}/relationship-actions",
        json={
            "action_type": "followup",
            "priority": "high",
            "status": "todo",
            "due_date": tomorrow_str
        }
    )
    action_id = create_response.json()["id"]
    
    # Complete the action
    response = requests.patch(
        f"{BASE_URL}/relationship-actions/{action_id}/complete"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None
    assert data["completed_at"].endswith("Z")


def test_complete_relationship_action_not_found():
    """Test complete returns 404 for non-existent action"""
    response = requests.patch(
        f"{BASE_URL}/relationship-actions/invalid-id/complete"
    )
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
