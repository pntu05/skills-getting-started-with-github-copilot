"""Tests for Mergington High School API endpoints"""
import pytest


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root URL redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # We have 9 activities in the database
        
    def test_get_activities_contains_expected_activities(self, client):
        """Test that specific activities are present"""
        response = client.get("/activities")
        data = response.json()
        
        # Check for expected activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Soccer Team" in data
        
    def test_get_activities_structure(self, client):
        """Test that each activity has the expected structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_valid_activity(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_when_already_registered(self, client):
        """Test that a student cannot sign up for the same activity twice"""
        email = "michael@mergington.edu"  # Already registered for Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is already signed up for this activity"
    
    def test_signup_multiple_students_to_same_activity(self, client):
        """Test that multiple different students can sign up for the same activity"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                "/activities/Programming Class/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all students were added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities["Programming Class"]["participants"]
        
        for email in emails:
            assert email in participants
    
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Art Club/signup",
            params={"email": "artist@mergington.edu"}
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_from_activity(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.post(
            "/activities/Basketball Team/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_when_not_registered(self, client):
        """Test unregister from an activity the student is not signed up for"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"
    
    def test_signup_and_unregister_workflow(self, client):
        """Test the complete workflow of signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Drama Club"
        
        # Step 1: Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Step 2: Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]


class TestActivityParticipants:
    """Tests for activity participant management"""
    
    def test_initial_participants_count(self, client):
        """Test that activities have the expected initial participant count"""
        response = client.get("/activities")
        activities = response.json()
        
        # Each activity should start with 2 participants
        for activity_name, activity_data in activities.items():
            assert len(activity_data["participants"]) == 2, \
                f"{activity_name} should have 2 initial participants"
    
    def test_participant_list_integrity(self, client):
        """Test that participant lists maintain integrity across operations"""
        email = "integrity@mergington.edu"
        
        # Get initial count for Swimming Club
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Swimming Club"]["participants"])
        
        # Add a participant
        client.post(
            "/activities/Swimming Club/signup",
            params={"email": email}
        )
        
        # Verify count increased by 1
        after_signup = client.get("/activities")
        new_count = len(after_signup.json()["Swimming Club"]["participants"])
        assert new_count == initial_count + 1
        
        # Remove the participant
        client.post(
            "/activities/Swimming Club/unregister",
            params={"email": email}
        )
        
        # Verify count returned to initial
        after_unregister = client.get("/activities")
        final_count = len(after_unregister.json()["Swimming Club"]["participants"])
        assert final_count == initial_count


class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_activity_name_with_spaces(self, client):
        """Test that activity names with spaces are handled correctly"""
        response = client.post(
            "/activities/Science Club/signup",
            params={"email": "science@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_email_format_variations(self, client):
        """Test that various email formats are accepted"""
        emails = [
            "simple@mergington.edu",
            "firstname.lastname@mergington.edu",
            "student123@mergington.edu",
            "test+tag@mergington.edu"
        ]
        
        activities_list = ["Chess Club", "Programming Class", "Gym Class", "Soccer Team"]
        
        for i, email in enumerate(emails):
            response = client.post(
                f"/activities/{activities_list[i]}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
    
    def test_case_sensitive_activity_names(self, client):
        """Test that activity names are case-sensitive"""
        response = client.post(
            "/activities/chess club/signup",  # lowercase
            params={"email": "test@mergington.edu"}
        )
        # Should fail because activity names are case-sensitive
        assert response.status_code == 404
