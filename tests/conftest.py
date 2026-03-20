"""
Pytest configuration and fixtures for FastAPI application tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities(client):
    """
    Fixture to reset activities to initial state before each test.
    This ensures test isolation by providing a fresh state for each test.
    """
    # Store original state
    from src.app import activities
    original_state = {
        name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy(),
        }
        for name, details in activities.items()
    }
    
    yield client
    
    # Restore original state after test
    activities.clear()
    activities.update(original_state)


@pytest.fixture
def sample_activity():
    """
    Fixture that provides sample test data for activities.
    """
    return {
        "name": "Chess Club",
        "email": "newstudent@mergington.edu"
    }
