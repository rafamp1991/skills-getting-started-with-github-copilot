"""
Tests for the FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the /activities endpoint"""
    
    def test_get_activities(self):
        """Test that we can fetch all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Check structure of an activity
        activity = list(activities.values())[0]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Test the signup endpoint"""
    
    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "test@example.com" in result["message"]
        assert "Chess Club" in result["message"]
    
    def test_signup_duplicate_student(self):
        """Test that a student cannot sign up twice for the same activity"""
        email = "duplicate@example.com"
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        result = response2.json()
        assert "already signed up" in result["detail"]
    
    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@example.com"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]


class TestUnregisterEndpoint:
    """Test the unregister endpoint"""
    
    def test_unregister_participant(self):
        """Test unregistering a participant from an activity"""
        email = "unregister@example.com"
        # First, sign up
        signup_response = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Then, unregister
        unregister_response = client.delete(
            f"/activities/Programming%20Class/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        result = unregister_response.json()
        assert "Unregistered" in result["message"]
        
        # Verify participant is no longer in the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Programming Class"]["participants"]
    
    def test_unregister_nonexistent_participant(self):
        """Test unregistering someone who is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@example.com"
        )
        assert response.status_code == 400
        result = response.json()
        assert "not registered" in result["detail"]
    
    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_redirect_to_static(self):
        """Test that root endpoint redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
