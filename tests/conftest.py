"""
Pytest configuration and fixtures for FastAPI tests
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """
    Arrange: Provide a test client for the FastAPI app
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Arrange: Provide a fresh copy of activities for each test
    This prevents test pollution where one test modifies the shared activities dict
    """
    # Save the original state
    original_state = copy.deepcopy(activities)
    
    yield activities
    
    # Restore the original state after the test
    activities.clear()
    activities.update(original_state)
