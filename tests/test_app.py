"""
Comprehensive test suite for the Mergington High School Activities API.
Tests cover GET /activities, POST signup, and DELETE unregister endpoints.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, reset_activities):
        """Test that GET /activities returns a 200 status code."""
        response = reset_activities.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, reset_activities):
        """Test that GET /activities returns a dictionary."""
        response = reset_activities.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_chess_club(self, reset_activities):
        """Test that Chess Club is in the returned activities."""
        response = reset_activities.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
    
    def test_activity_has_required_fields(self, reset_activities):
        """Test that each activity has required fields."""
        response = reset_activities.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_participants_are_strings(self, reset_activities):
        """Test that all participants are email strings."""
        response = reset_activities.get("/activities")
        activities = response.json()
        
        for activity_data in activities.values():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation
    
    def test_max_participants_is_positive_integer(self, reset_activities):
        """Test that max_participants is a positive integer."""
        response = reset_activities.get("/activities")
        activities = response.json()
        
        for activity_data in activities.values():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_student_returns_200(self, reset_activities, sample_activity):
        """Test successful signup of a new student."""
        response = reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        assert response.status_code == 200
    
    def test_signup_returns_success_message(self, reset_activities, sample_activity):
        """Test that signup returns a success message."""
        response = reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert sample_activity["email"] in data["message"]
    
    def test_signup_for_nonexistent_activity_returns_404(self, reset_activities):
        """Test that signup for non-existent activity returns 404."""
        response = reset_activities.post(
            "/activities/NonexistentClub/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_email_returns_400(self, reset_activities, sample_activity):
        """Test that duplicate signup attempt returns 400."""
        # First signup should succeed
        response1 = reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_adds_participant_to_activity(self, reset_activities, sample_activity):
        """Test that signup actually adds the participant to the activity."""
        # Get initial participant count
        response_before = reset_activities.get("/activities")
        initial_count = len(response_before.json()[sample_activity["name"]]["participants"])
        
        # Sign up new student
        reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        
        # Get updated participant count
        response_after = reset_activities.get("/activities")
        updated_count = len(response_after.json()[sample_activity["name"]]["participants"])
        
        assert updated_count == initial_count + 1
        assert sample_activity["email"] in response_after.json()[sample_activity["name"]]["participants"]
    
    def test_signup_multiple_students_to_same_activity(self, reset_activities, sample_activity):
        """Test that multiple students can sign up for the same activity."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": email1}
        )
        assert response1.status_code == 200
        
        response2 = reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": email2}
        )
        assert response2.status_code == 200
        
        # Verify both are in the activity
        activities_response = reset_activities.get("/activities")
        participants = activities_response.json()[sample_activity["name"]]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""
    
    def test_unregister_existing_participant_returns_200(self, reset_activities, sample_activity):
        """Test successful unregister of an existing participant."""
        # First sign up
        reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        
        # Then unregister
        response = reset_activities.delete(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        assert response.status_code == 200
    
    def test_unregister_returns_success_message(self, reset_activities, sample_activity):
        """Test that unregister returns a success message."""
        # First sign up
        reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        
        # Then unregister
        response = reset_activities.delete(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert sample_activity["email"] in data["message"]
    
    def test_unregister_from_nonexistent_activity_returns_404(self, reset_activities):
        """Test that unregister from non-existent activity returns 404."""
        response = reset_activities.delete(
            "/activities/NonexistentClub/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_nonexistent_participant_returns_400(self, reset_activities, sample_activity):
        """Test that unregistering a non-signed-up student returns 400."""
        response = reset_activities.delete(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_removes_participant_from_activity(self, reset_activities, sample_activity):
        """Test that unregister actually removes the participant from the activity."""
        # Sign up
        reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        
        # Get count before unregister
        response_before = reset_activities.get("/activities")
        count_before = len(response_before.json()[sample_activity["name"]]["participants"])
        
        # Unregister
        reset_activities.delete(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        
        # Get count after unregister
        response_after = reset_activities.get("/activities")
        count_after = len(response_after.json()[sample_activity["name"]]["participants"])
        
        assert count_after == count_before - 1
        assert sample_activity["email"] not in response_after.json()[sample_activity["name"]]["participants"]
    
    def test_signup_after_unregister(self, reset_activities, sample_activity):
        """Test that a student can sign up again after unregistering."""
        # Sign up
        response1 = reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = reset_activities.delete(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": sample_activity["email"]}
        )
        assert response3.status_code == 200
        
        # Verify in activity
        activities_response = reset_activities.get("/activities")
        assert sample_activity["email"] in activities_response.json()[sample_activity["name"]]["participants"]
    
    def test_unregister_other_participants_unaffected(self, reset_activities, sample_activity):
        """Test that unregistering one student doesn't affect others."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Both sign up
        reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": email1}
        )
        reset_activities.post(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": email2}
        )
        
        # Unregister first student
        reset_activities.delete(
            f"/activities/{sample_activity['name']}/signup",
            params={"email": email1}
        )
        
        # Verify second student still there
        response = reset_activities.get("/activities")
        participants = response.json()[sample_activity["name"]]["participants"]
        assert email1 not in participants
        assert email2 in participants
