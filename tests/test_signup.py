"""
Tests for POST /activities/{activity_name}/signup endpoint
"""

import pytest


class TestSignupSuccess:
    """Tests for successful signup scenarios"""

    def test_signup_new_student_success(self, client, fresh_activities):
        """
        Arrange: A new student email and valid activity
        Act: Sign up the student for the activity
        Assert: Verify success response and participant was added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in fresh_activities[activity_name]["participants"]

    def test_signup_increments_participant_count(self, client, fresh_activities):
        """
        Arrange: Track initial participant count
        Act: Sign up a new student
        Assert: Verify participant count increased by 1
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "newplayer@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_multiple_students_different_emails(self, client, fresh_activities):
        """
        Arrange: Multiple unique emails
        Act: Sign up each student
        Assert: All are added to the activity
        """
        # Arrange
        activity_name = "Art Studio"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]

        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert
        for email in emails:
            assert email in fresh_activities[activity_name]["participants"]


class TestSignupValidationErrors:
    """Tests for signup validation errors"""

    def test_signup_duplicate_student_fails(self, client, fresh_activities):
        """
        Arrange: A student already signed up
        Act: Try to sign up the same student again
        Assert: Verify 400 error with appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client, fresh_activities):
        """
        Arrange: An activity that doesn't exist
        Act: Try to sign up for that activity
        Assert: Verify 404 error with appropriate message
        """
        # Arrange
        activity_name = "Nonexistent Activity Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_activity_full_fails(self, client, fresh_activities):
        """
        Arrange: An activity at max capacity
        Act: Try to sign up a new student
        Assert: Verify 400 error indicating activity is full
        """
        # Arrange
        activity_name = "Tennis Club"
        # Tennis Club has max_participants of 10 and 2 participants, so we have room
        # Let's first fill it up
        email_template = "student_{}.@mergington.edu"
        for i in range(fresh_activities[activity_name]["max_participants"] - len(fresh_activities[activity_name]["participants"])):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email_template.format(i)}
            )

        # Now try to add one more
        final_email = "onemorestudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": final_email}
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"]


class TestSignupEdgeCases:
    """Tests for signup edge cases"""

    def test_signup_with_url_encoded_activity_name(self, client, fresh_activities):
        """
        Arrange: Activity name with spaces
        Act: Sign up using URL encoding
        Assert: Verify signup works with encoded names
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newmember@mergington.edu"

        # Act
        response = client.post(
            f"/activities/Chess%20Club/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200

    def test_signup_adds_to_correct_activity(self, client, fresh_activities):
        """
        Arrange: Multiple activities and a new student
        Act: Sign up for one activity
        Assert: Verify only that activity was modified
        """
        # Arrange
        target_activity = "Drama Club"
        other_activity = "Science Club"
        email = "actor@mergington.edu"
        other_participants_before = len(fresh_activities[other_activity]["participants"])

        # Act
        response = client.post(
            f"/activities/{target_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in fresh_activities[target_activity]["participants"]
        assert len(fresh_activities[other_activity]["participants"]) == other_participants_before

    def test_signup_response_message_format(self, client, fresh_activities):
        """
        Arrange: A signup request
        Act: Sign up a student
        Assert: Verify response message has correct format
        """
        # Arrange
        activity_name = "Debate Team"
        email = "speaker@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        message = response.json()["message"]
        assert email in message
        assert activity_name in message
