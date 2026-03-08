"""
Integration tests for multi-endpoint workflows
"""

import pytest


class TestIntegrationSignupAndRemoval:
    """Integration tests for complete signup and removal workflows"""

    def test_signup_then_remove_complete_workflow(self, client, fresh_activities):
        """
        Arrange: A new student and an activity
        Act: Sign up the student, then remove them
        Assert: Verify both operations succeed and state changes are correct
        """
        # Arrange
        activity_name = "Chess Club"
        email = "workflow@mergington.edu"
        initial_participants = len(fresh_activities[activity_name]["participants"])

        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert signup
        assert signup_response.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_participants + 1

        # Act - Remove
        remove_response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert remove
        assert remove_response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_participants

    def test_signup_remove_signup_again(self, client, fresh_activities):
        """
        Arrange: A student who will signup, remove, and signup again
        Act: Perform all three operations
        Assert: Verify all succeed and state is consistent
        """
        # Arrange
        activity_name = "Drama Club"
        email = "actor@mergington.edu"

        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]

        # Act - Remove
        response2 = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response2.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]

        # Act - Signup again
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Second signup should succeed
        assert response3.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]

    def test_multiple_students_signup_and_remove(self, client, fresh_activities):
        """
        Arrange: Multiple students
        Act: Sign them up, verify, remove one, verify
        Assert: Correct students remain and removed student is gone
        """
        # Arrange
        activity_name = "Science Club"
        emails = ["scientist1@mergington.edu", "scientist2@mergington.edu", "scientist3@mergington.edu"]

        # Act - Sign up all
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert - All signed up
        for email in emails:
            assert email in fresh_activities[activity_name]["participants"]

        # Act - Remove middle student
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{emails[1]}"
        )

        # Assert - Only middle student removed
        assert remove_response.status_code == 200
        assert emails[0] in fresh_activities[activity_name]["participants"]
        assert emails[1] not in fresh_activities[activity_name]["participants"]
        assert emails[2] in fresh_activities[activity_name]["participants"]


class TestIntegrationActivityCapacity:
    """Integration tests for activity capacity management"""

    def test_fill_activity_to_capacity(self, client, fresh_activities):
        """
        Arrange: An activity and enough new students to fill it
        Act: Sign up students until activity is full
        Assert: Verify activity fills correctly and rejects additional signups
        """
        # Arrange
        activity_name = "Tennis Club"
        max_capacity = fresh_activities[activity_name]["max_participants"]
        current_participants = len(fresh_activities[activity_name]["participants"])
        spots_available = max_capacity - current_participants

        # Act - Fill remaining spots
        for i in range(spots_available):
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"player{i}@mergington.edu"}
            )
            assert response.status_code == 200

        # Assert - Activity is full
        assert len(fresh_activities[activity_name]["participants"]) == max_capacity

        # Act - Try to add one more
        response_overfull = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "extrastudent@mergington.edu"}
        )

        # Assert - Rejection
        assert response_overfull.status_code == 400
        assert "full" in response_overfull.json()["detail"]
        assert len(fresh_activities[activity_name]["participants"]) == max_capacity

    def test_remove_opens_activity_spot(self, client, fresh_activities):
        """
        Arrange: Fill an activity to capacity
        Act: Remove one participant, then try to add a new one
        Assert: Verify the new signup succeeds after removal
        """
        # Arrange
        activity_name = "Basketball Team"
        new_student = "newplayer@mergington.edu"
        existing_student = "alex@mergington.edu"

        # First fill to capacity (manually add if needed)
        max_capacity = fresh_activities[activity_name]["max_participants"]
        current_count = len(fresh_activities[activity_name]["participants"])
        
        # Add students to fill capacity
        for i in range(max_capacity - current_count):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"filler{i}@mergington.edu"}
            )

        assert len(fresh_activities[activity_name]["participants"]) == max_capacity

        # Act - Remove existing student
        client.delete(f"/activities/{activity_name}/participants/{existing_student}")

        # Assert - Should have one spot open
        assert len(fresh_activities[activity_name]["participants"]) == max_capacity - 1

        # Act - Add new student
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )

        # Assert - New signup succeeds
        assert response.status_code == 200
        assert new_student in fresh_activities[activity_name]["participants"]


class TestIntegrationDataIsolation:
    """Integration tests for data isolation between activities"""

    def test_activities_isolated_from_each_other(self, client, fresh_activities):
        """
        Arrange: Two different activities
        Act: Modify one activity
        Assert: Verify other activity is unaffected
        """
        # Arrange
        activity1 = "Gym Class"
        activity2 = "Programming Class"
        email = "newstudent@mergington.edu"
        activity2_initial_count = len(fresh_activities[activity2]["participants"])

        # Act - Sign up only for activity1
        response = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in fresh_activities[activity1]["participants"]
        assert email not in fresh_activities[activity2]["participants"]
        assert len(fresh_activities[activity2]["participants"]) == activity2_initial_count

    def test_participant_not_in_multiple_activities(self, client, fresh_activities):
        """
        Arrange: A student who attempts to be in multiple activities
        Act: Sign up for different activities
        Assert: Verify signup succeeds for each but removing from one doesn't affect others
        """
        # Arrange
        email = "multiactivity@mergington.edu"
        activity1 = "Debate Team"
        activity2 = "Art Studio"

        # Act - Sign up for both
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )

        # Assert - Both signups succeeded
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Act - Remove from activity1
        response_remove = client.delete(f"/activities/{activity1}/participants/{email}")

        # Assert - Removal succeeded for activity1 but not activity2
        assert response_remove.status_code == 200
        assert email not in fresh_activities[activity1]["participants"]
        assert email in fresh_activities[activity2]["participants"]
