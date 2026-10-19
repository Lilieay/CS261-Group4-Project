import http.client
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

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


def test_real_tu_refusal_returns_401_without_creating_session():
    from app.services.auth import ACTIVE_SESSIONS

    cases = [
        ({}, b'{"status":false}', None),
        ({}, b'{"status":true,"type":"employee","displayname_en":"Staff"}', None),
        ({}, b'{"status":true,"type":"student"}', None),
        ({"TU_API_KEY": ""}, None, None),
        ({}, None, OSError("offline")),
        ({"TU_API_URL": "not-a-url"}, None, None),
        ({}, None, http.client.IncompleteRead(b"partial", 10)),
        ({}, None, http.client.InvalidURL("bad URL")),
        ({}, None, http.client.BadStatusLine("malformed status")),
    ]
    for overrides, body, network_error in cases:
        before = dict(ACTIVE_SESSIONS)
        with patch.dict(
            os.environ,
            {
                "TU_API_MODE": "real",
                "TU_API_URL": "https://tu.example.test/auth",
                "TU_API_KEY": "test-application-key",
                "TU_API_TIMEOUT": "5",
                **overrides,
            },
        ), patch("app.services.tu_api.urlopen") as urlopen:
            if isinstance(network_error, http.client.IncompleteRead):
                urlopen.return_value.__enter__.return_value.status = 200
                urlopen.return_value.__enter__.return_value.read.side_effect = network_error
            elif network_error:
                urlopen.side_effect = network_error
            elif body is not None:
                urlopen.return_value.__enter__.return_value.status = 200
                urlopen.return_value.__enter__.return_value.read.return_value = body
            response = client.post(
                "/api/auth/login",
                json={"username": "6800000000", "password": "wrong"},
            )

        assert response.status_code == 401
        assert ACTIVE_SESSIONS == before
