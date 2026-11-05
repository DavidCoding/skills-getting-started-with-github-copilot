from copy import deepcopy
from importlib import import_module

import pytest
from fastapi.testclient import TestClient


app_module = import_module("src.app")

ACTIVITY_NAME = "Chess Club"
EXISTING_PARTICIPANT = "existing@mergington.edu"
TEST_ACTIVITIES = {
    ACTIVITY_NAME: {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": [EXISTING_PARTICIPANT],
    }
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(TEST_ACTIVITIES))
    return TestClient(app_module.app)


def test_get_activities_returns_activity_details_and_participants(client):
    # Arrange
    expected_participants = [EXISTING_PARTICIPANT]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[ACTIVITY_NAME]["participants"] == expected_participants


def test_signup_adds_participant(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in app_module.activities[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = EXISTING_PARTICIPANT

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "new@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = EXISTING_PARTICIPANT

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities[ACTIVITY_NAME]["participants"]


def test_unregister_returns_not_found_for_missing_signup(client):
    # Arrange
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": EXISTING_PARTICIPANT},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
