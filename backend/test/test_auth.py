from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.main import app
from app.routers.auth import get_auth_service
from app.services.auth import AuthService
from app.services.tu_api import TUAccount


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    service = AuthService(
        session_factory,
        verify=lambda username, password: (
            TUAccount(username, "Student User", "student", True)
            if password == "password123"
            else None
        ),
    )
    app.dependency_overrides[get_auth_service] = lambda: service
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_login_success_and_status(client: TestClient):
    response = client.post("/api/auth/login", json={"username": "student", "password": "password123"})
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["username"] == "student"
    assert body["access_token"]

    status_response = client.get("/api/auth/status", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert status_response.status_code == 200
    assert status_response.json()["logged_in"] is True


def test_login_rejects_wrong_password(client: TestClient):
    response = client.post("/api/auth/login", json={"username": "student", "password": "wrong"})
    assert response.status_code == 401


def test_logout_invalidates_token(client: TestClient):
    login_response = client.post("/api/auth/login", json={"username": "student", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_repeated_login_reuses_database_user(client: TestClient):
    first = client.post(
        "/api/auth/login",
        json={"username": "student", "password": "password123"},
    ).json()
    second = client.post(
        "/api/auth/login",
        json={"username": "student", "password": "password123"},
    ).json()

    assert first["user"]["id"] == second["user"]["id"]
    assert first["user"]["id"] == 1


def test_rejected_login_does_not_create_database_user(client: TestClient):
    response = client.post(
        "/api/auth/login",
        json={"username": "unknown", "password": "wrong"},
    )

    assert response.status_code == 401
    successful_login = client.post(
        "/api/auth/login",
        json={"username": "student", "password": "password123"},
    )
    assert successful_login.json()["user"]["id"] == 1


def test_database_failure_does_not_issue_login_token(client: TestClient):
    def unavailable_session():
        raise SQLAlchemyError("database unavailable")

    service = AuthService(
        unavailable_session,
        verify=lambda username, _password: TUAccount(
            username, "Student User", "student", True
        ),
    )
    app.dependency_overrides[get_auth_service] = lambda: service

    response = client.post(
        "/api/auth/login",
        json={"username": "student", "password": "password123"},
    )

    assert response.status_code == 503
    assert "access_token" not in response.json()
