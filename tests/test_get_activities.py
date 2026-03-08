"""
Tests for GET /activities endpoint
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_success(self, client, fresh_activities):
        """
        Arrange: Activities are pre-populated in the app
        Act: Make a GET request to /activities
        Assert: Verify all activities are returned with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) > 0

    def test_get_activities_returns_all_required_activities(self, client, fresh_activities):
        """
        Arrange: Activity names we expect to find
        Act: Fetch all activities
        Assert: Verify all expected activities are present
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Debate Team",
            "Art Studio",
            "Drama Club",
            "Science Club"
        ]

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name in expected_activities:
            assert activity_name in activities_data

    def test_get_activities_has_required_fields(self, client, fresh_activities):
        """
        Arrange: Expected activity structure
        Act: Fetch activities
        Assert: Verify each activity has required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name, activity_details in activities_data.items():
            for field in required_fields:
                assert field in activity_details, f"Missing {field} in {activity_name}"

    def test_get_activities_participants_is_list(self, client, fresh_activities):
        """
        Arrange: Expect participants to be a list
        Act: Fetch activities
        Assert: Verify participants field is always a list
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name, activity_details in activities_data.items():
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_max_participants_is_int(self, client, fresh_activities):
        """
        Arrange: Expect max_participants to be an integer
        Act: Fetch activities
        Assert: Verify max_participants field is an integer
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name, activity_details in activities_data.items():
            assert isinstance(activity_details["max_participants"], int)
            assert activity_details["max_participants"] > 0
