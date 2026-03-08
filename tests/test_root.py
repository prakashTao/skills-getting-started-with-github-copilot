"""
Tests for GET / (root redirect endpoint)
"""

import pytest


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_index(self, client, fresh_activities):
        """
        Arrange: No setup needed
        Act: Make a GET request to /
        Assert: Verify redirect status and location header
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_follows_to_html(self, client, fresh_activities):
        """
        Arrange: No setup needed
        Act: Make a GET request to / with follow_redirects=True
        Assert: Verify we eventually get an HTML response
        """
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
