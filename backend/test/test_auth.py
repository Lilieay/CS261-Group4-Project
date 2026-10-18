from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_success_and_status():
    response = client.post("/api/auth/login", json={"username": "6800000000", "password": "0000000000000"})
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["username"] == "6800000000"
    assert body["access_token"]

    status_response = client.get("/api/auth/status", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert status_response.status_code == 200
    assert status_response.json()["logged_in"] is True


def test_login_rejects_wrong_password():
    response = client.post("/api/auth/login", json={"username": "6800000000", "password": "wrong"})
    assert response.status_code == 401


def test_logout_invalidates_token():
    login_response = client.post("/api/auth/login", json={"username": "6800000000", "password": "0000000000000"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401
