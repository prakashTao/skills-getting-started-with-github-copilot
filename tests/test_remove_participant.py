"""
Tests for DELETE /activities/{activity_name}/participants/{email} endpoint
"""

import pytest


class TestRemoveParticipantSuccess:
    """Tests for successful participant removal"""

    def test_remove_existing_participant_success(self, client, fresh_activities):
        """
        Arrange: An existing participant in an activity
        Act: Delete that participant
        Assert: Verify success response and participant was removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        assert email in fresh_activities[activity_name]["participants"]

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email not in fresh_activities[activity_name]["participants"]

    def test_remove_decrements_participant_count(self, client, fresh_activities):
        """
        Arrange: Track initial participant count
        Act: Remove a participant
        Assert: Verify participant count decreased by 1
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_last_participant(self, client, fresh_activities):
        """
        Arrange: An activity with only one participant
        Act: Remove that participant
        Assert: Verify activity is now empty
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        # This activity has only one participant
        assert len(fresh_activities[activity_name]["participants"]) == 1

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == 0

    def test_remove_leaves_other_participants_intact(self, client, fresh_activities):
        """
        Arrange: An activity with multiple participants
        Act: Remove one participant
        Assert: Verify other participants remain
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        other_email = "daniel@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email_to_remove}")

        # Assert
        assert response.status_code == 200
        assert email_to_remove not in fresh_activities[activity_name]["participants"]
        assert other_email in fresh_activities[activity_name]["participants"]


class TestRemoveParticipantErrors:
    """Tests for removal error scenarios"""

    def test_remove_nonexistent_participant_fails(self, client, fresh_activities):
        """
        Arrange: A participant who is not signed up
        Act: Try to remove them
        Assert: Verify 400 error with appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notastudent@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_fails(self, client, fresh_activities):
        """
        Arrange: An activity that doesn't exist
        Act: Try to remove a participant from it
        Assert: Verify 404 error with appropriate message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRemoveParticipantEdgeCases:
    """Tests for removal edge cases"""

    def test_remove_with_url_encoded_activity_name(self, client, fresh_activities):
        """
        Arrange: Activity name with spaces that needs URL encoding
        Act: Remove participant using encoded name
        Assert: Verify removal works with encoded names
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/Chess%20Club/participants/{email}")

        # Assert
        assert response.status_code == 200

    def test_remove_with_special_characters_in_email(self, client, fresh_activities):
        """
        Arrange: Email with special characters that needs encoding
        Act: Remove participant with special email
        Assert: Verify removal works with encoded emails
        """
        # Arrange
        activity_name = "Art Studio"
        email = "rachel@mergington.edu"

        # Act - URL encode the email parameter
        response = client.delete(
            f"/activities/{activity_name}/participants/rachel%40mergington.edu"
        )

        # Assert
        assert response.status_code == 200

    def test_remove_does_not_affect_other_activities(self, client, fresh_activities):
        """
        Arrange: A participant in multiple activities (not currently possible, but good to verify isolation)
        Act: Remove from one activity
        Assert: Verify other activities are unaffected
        """
        # Arrange
        email = "michael@mergington.edu"  # in Chess Club
        other_activity = "Gym Class"
        
        # Act
        response = client.delete(f"/activities/Chess Club/participants/{email}")

        # Assert
        assert response.status_code == 200
        # Verify the email is NOT in Chess Club anymore (if they were)
        # And that other activities are untouched
        assert len(fresh_activities[other_activity]["participants"]) > 0

    def test_remove_response_message_format(self, client, fresh_activities):
        """
        Arrange: A removal request
        Act: Remove a participant
        Assert: Verify response message has correct format
        """
        # Arrange
        activity_name = "Debate Team"
        email = "chris@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        message = response.json()["message"]
        assert email in message
        assert activity_name in message
