from collections.abc import Iterator
import http.client
import os
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.main import app
from app.models.user import User
from app.routers.auth import get_auth_service
from app.services.auth import AuthService
from app.services.tu_api import TUAccount


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    try:
        yield factory
    finally:
        engine.dispose()


@pytest.fixture
def client(session_factory) -> Iterator[TestClient]:
    previous_override = app.dependency_overrides.get(get_auth_service)
    service = AuthService(
        session_factory,
        verify=lambda username, password: (
            TUAccount(username, "Student User", "student", True)
            if password == "0000000000000"
            else None
        ),
    )
    app.dependency_overrides[get_auth_service] = lambda: service
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_auth_service, None)
        else:
            app.dependency_overrides[get_auth_service] = previous_override


def test_login_success_and_status(client: TestClient):
    response = client.post(
        "/api/auth/login",
        json={"username": "6800000000", "password": "0000000000000"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["username"] == "6800000000"
    assert body["user"]["id"] > 0
    assert body["access_token"]

    status_response = client.get(
        "/api/auth/status",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["logged_in"] is True


def test_login_rejects_wrong_password(client: TestClient, session_factory):
    response = client.post(
        "/api/auth/login",
        json={"username": "6800000000", "password": "wrong"},
    )
    assert response.status_code == 401
    assert "access_token" not in response.json()
    with session_factory() as session:
        assert session.scalar(select(func.count(User.id))) == 0


def test_logout_invalidates_token(client: TestClient):
    login_response = client.post(
        "/api/auth/login",
        json={"username": "6800000000", "password": "0000000000000"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_repeated_login_reuses_database_user(client: TestClient):
    payload = {"username": "6800000000", "password": "0000000000000"}
    first = client.post("/api/auth/login", json=payload).json()
    second = client.post("/api/auth/login", json=payload).json()

    assert first["user"]["id"] == second["user"]["id"]
    assert first["user"]["id"] > 0


def test_database_failure_does_not_issue_login_token(client: TestClient):
    def unavailable_session():
        raise SQLAlchemyError("database unavailable")

    previous_override = app.dependency_overrides[get_auth_service]
    service = AuthService(
        unavailable_session,
        verify=lambda username, _password: TUAccount(
            username, "Student User", "student", True
        ),
    )
    app.dependency_overrides[get_auth_service] = lambda: service
    try:
        response = client.post(
            "/api/auth/login",
            json={"username": "6800000000", "password": "0000000000000"},
        )
    finally:
        app.dependency_overrides[get_auth_service] = previous_override

    assert response.status_code == 503
    assert "access_token" not in response.json()


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body
        self.status = 200

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        return False

    def read(self):
        return self.body


@pytest.mark.parametrize(
    "overrides,body,network_error",
    [
        ({}, b'{"status":false}', None),
        ({}, b'{"status":true,"type":"employee","displayname_en":"Staff"}', None),
        ({}, b'{"status":true,"type":"student"}', None),
        ({"TU_API_KEY": ""}, None, None),
        ({}, None, OSError("offline")),
        ({"TU_API_URL": "not-a-url"}, None, None),
        ({}, None, http.client.IncompleteRead(b"partial", 10)),
        ({}, None, http.client.InvalidURL("bad URL")),
        ({}, None, http.client.BadStatusLine("malformed status")),
    ],
)
def test_real_tu_refusal_returns_401_without_persisting_user(
    client: TestClient,
    session_factory,
    overrides: dict[str, str],
    body: bytes | None,
    network_error: Exception | None,
):
    real_service = AuthService(session_factory)
    previous_override = app.dependency_overrides[get_auth_service]
    app.dependency_overrides[get_auth_service] = lambda: real_service
    try:
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
                urlopen.return_value = FakeResponse(b"")
                urlopen.return_value.read = Mock(side_effect=network_error)
            elif network_error:
                urlopen.side_effect = network_error
            elif body is not None:
                urlopen.return_value = FakeResponse(body)
            response = client.post(
                "/api/auth/login",
                json={"username": "6800000000", "password": "0000000000000"},
            )
    finally:
        app.dependency_overrides[get_auth_service] = previous_override

    assert response.status_code == 401
    assert "access_token" not in response.json()
    with session_factory() as session:
        assert session.scalar(select(func.count(User.id))) == 0
