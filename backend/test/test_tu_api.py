from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_tu_mock_verification_success():
    response = client.post(
        "/api/auth/verify-tu",
        json={"username": "mock_student", "password": "mock_password"},
    )
    assert response.status_code == 200
    assert response.json()["verified"] is True
    assert response.json()["source"] == "mock"


def test_tu_mock_verification_failure():
    response = client.post(
        "/api/auth/verify-tu",
        json={"username": "wrong_user", "password": "wrong_password"},
    )
    assert response.status_code == 200
    assert response.json()["verified"] is False


def test_tu_verification_requires_both_fields():
    response = client.post("/api/auth/verify-tu", json={"username": "mock_student"})
    assert response.status_code == 422
