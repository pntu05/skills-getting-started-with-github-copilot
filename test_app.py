"""
Tests for High School Management System API
"""

from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_update_activity_success():
    """Test successfully updating an activity"""
    # Update Chess Club description
    response = client.put(
        "/activities/Chess Club",
        params={"description": "Advanced chess strategies and tournaments"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Updated Chess Club"
    assert data["activity"]["description"] == "Advanced chess strategies and tournaments"
    
    # Reset the activity
    activities["Chess Club"]["description"] = "Learn strategies and compete in chess tournaments"


def test_update_activity_schedule():
    """Test updating activity schedule"""
    response = client.put(
        "/activities/Programming Class",
        params={"schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["activity"]["schedule"] == "Mondays and Wednesdays, 4:00 PM - 5:00 PM"
    
    # Reset the activity
    activities["Programming Class"]["schedule"] = "Tuesdays and Thursdays, 3:30 PM - 4:30 PM"


def test_update_activity_max_participants():
    """Test updating max participants"""
    response = client.put(
        "/activities/Gym Class",
        params={"max_participants": 25}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["activity"]["max_participants"] == 25
    
    # Reset the activity
    activities["Gym Class"]["max_participants"] = 30


def test_update_activity_multiple_fields():
    """Test updating multiple fields at once"""
    response = client.put(
        "/activities/Chess Club",
        params={
            "description": "Competitive chess training",
            "schedule": "Saturdays, 2:00 PM - 4:00 PM",
            "max_participants": 15
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["activity"]["description"] == "Competitive chess training"
    assert data["activity"]["schedule"] == "Saturdays, 2:00 PM - 4:00 PM"
    assert data["activity"]["max_participants"] == 15
    
    # Reset the activity
    activities["Chess Club"]["description"] = "Learn strategies and compete in chess tournaments"
    activities["Chess Club"]["schedule"] = "Fridays, 3:30 PM - 5:00 PM"
    activities["Chess Club"]["max_participants"] = 12


def test_update_activity_not_found():
    """Test updating a non-existent activity"""
    response = client.put(
        "/activities/NonExistent Activity",
        params={"description": "This should fail"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_activity_success():
    """Test successfully deleting an activity"""
    # First, add a temporary activity to delete
    activities["Temp Activity"] = {
        "description": "Temporary activity for testing",
        "schedule": "Test schedule",
        "max_participants": 10,
        "participants": []
    }
    
    response = client.delete("/activities/Temp Activity")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Deleted Temp Activity"
    assert "Temp Activity" not in activities


def test_delete_activity_not_found():
    """Test deleting a non-existent activity"""
    response = client.delete("/activities/NonExistent Activity")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
