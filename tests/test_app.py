"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_state)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that GET /activities returns status code 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_chess_club(self, client, reset_activities):
        """Test that activities include Chess Club"""
        response = client.get("/activities")
        activities_data = response.json()
        assert "Chess Club" in activities_data
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that activity objects have required fields"""
        response = client.get("/activities")
        activities_data = response.json()
        chess_club = activities_data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_get_activities_participants_is_list(self, client, reset_activities):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities_data = response.json()
        assert isinstance(activities_data["Chess Club"]["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_returns_200(self, client, reset_activities):
        """Test successful signup returns 200"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds participant to activity"""
        new_email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={new_email}")
        
        response = client.get("/activities")
        activities_data = response.json()
        assert new_email in activities_data["Chess Club"]["participants"]
    
    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered_returns_400(self, client, reset_activities):
        """Test that signup for already registered student returns 400"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test signing up multiple students"""
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Programming%20Class/signup?email={email}"
            )
            assert response.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()["Programming Class"]["participants"]
        
        for email in emails:
            assert email in participants


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_returns_200(self, client, reset_activities):
        """Test unregistering an existing participant returns 200"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes participant from activity"""
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        activities_data = response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test that unregister returns a success message"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test unregistering from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered_participant_returns_400(self, client, reset_activities):
        """Test unregistering non-registered participant returns 400"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering multiple participants"""
        emails_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        for email in emails_to_remove:
            response = client.delete(
                f"/activities/Chess%20Club/unregister?email={email}"
            )
            assert response.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        
        assert len(participants) == 0


class TestSignupAndUnregisterWorkflow:
    """Integration tests for signup and unregister workflows"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "workflow@mergington.edu"
        
        # Signup
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()["Chess Club"]["participants"]
    
    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        """Test multiple signup and unregister operations"""
        activity = "Programming Class"
        emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]
        
        # Sign up all
        for email in emails:
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all are signed up
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
        
        # Unregister some
        for email in emails[:2]:
            response = client.delete(
                f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
            )
            assert response.status_code == 200
        
        # Verify correct participants remain
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert emails[0] not in participants
        assert emails[1] not in participants
        assert emails[2] in participants
