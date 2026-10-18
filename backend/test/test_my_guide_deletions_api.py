from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.dao.delete_owned_guide_dao import DeleteOwnedGuideDAO
from app.db import Base, get_db_session
from app.main import app
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User
from app.routers.auth import get_auth_service
from app.services.auth import AuthService
from app.services.tu_api import TUAccount


@pytest.fixture
def api() -> Iterator[tuple[TestClient, Session, dict[str, int]]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    connection = engine.connect()
    transaction = connection.begin()
    Base.metadata.create_all(connection)
    session = Session(connection, join_transaction_mode="create_savepoint")

    owner = User(username="6800000000", displayname_th="เจ้าของทดสอบ")
    other = User(username="admin", displayname_th="ผู้ใช้อื่น")
    course = Course(course_code="CS261", course_name="Software Engineering")
    session.add_all([owner, other, course])
    session.flush()
    owned = Guide(
        course_id=course.id,
        publisher_id=owner.id,
        title="แนวข้อสอบของเจ้าของ",
        academic_year=2568,
        semester=1,
        exam_period="midterm",
        topics="ข้อมูลทดสอบ",
        exam_format="mixed",
    )
    other_owned = Guide(
        course_id=course.id,
        publisher_id=other.id,
        title="แนวข้อสอบของผู้ใช้อื่น",
        academic_year=2568,
        semester=2,
        exam_period="final",
        topics="ข้อมูลส่วนตัว",
        exam_format="objective",
        objective_count=10,
    )
    session.add_all([owned, other_owned])
    session.commit()
    ids = {
        "owned_guide": owned.id,
        "other_guide": other_owned.id,
        "owner": owner.id,
        "other": other.id,
    }

    def override_db_session():
        yield session

    previous_db_override = app.dependency_overrides.get(get_db_session)
    previous_auth_override = app.dependency_overrides.get(get_auth_service)
    app.dependency_overrides[get_db_session] = override_db_session

    @contextmanager
    def auth_session():
        yield session

    auth_service = AuthService(
        auth_session,
        verify=lambda username, password: (
            TUAccount(username, username, "student", True)
            if password == "0000000000000"
            else None
        ),
    )
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    try:
        with TestClient(app) as client:
            yield client, session, ids
    finally:
        if previous_db_override is None:
            app.dependency_overrides.pop(get_db_session, None)
        else:
            app.dependency_overrides[get_db_session] = previous_db_override
        if previous_auth_override is None:
            app.dependency_overrides.pop(get_auth_service, None)
        else:
            app.dependency_overrides[get_auth_service] = previous_auth_override
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def login(client: TestClient, username: str = "6800000000") -> str:
    password = "0000000000000"
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def guide_ids(session: Session) -> set[int]:
    return set(session.scalars(select(Guide.id)).all())


def test_owner_can_delete_guide_and_receives_confirmation(api):
    client, session, ids = api
    token = login(client)

    response = client.delete(
        f"/api/my-guides/{ids['owned_guide']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": ids["owned_guide"],
        "message": "ลบแนวข้อสอบสำเร็จ",
    }
    assert guide_ids(session) == {ids["other_guide"]}


def test_delete_requires_login(api):
    client, _, ids = api

    response = client.delete(f"/api/my-guides/{ids['owned_guide']}")

    assert response.status_code == 401
    assert response.json()["detail"] == "กรุณาส่ง Bearer token เพื่อยืนยันตัวตน"


def test_delete_rejects_invalid_token(api):
    client, _, ids = api

    response = client.delete(
        f"/api/my-guides/{ids['owned_guide']}",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token ไม่ถูกต้องหรือหมดอายุ"


def test_non_owner_cannot_delete_another_users_guide(api):
    client, session, ids = api
    token = login(client, "admin")
    before = guide_ids(session)

    response = client.delete(
        f"/api/my-guides/{ids['owned_guide']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "GUIDE_NOT_FOUND"
    assert guide_ids(session) == before


def test_missing_guide_returns_not_found_without_changing_data(api):
    client, session, ids = api
    token = login(client)
    before = guide_ids(session)

    response = client.delete(
        "/api/my-guides/99999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "GUIDE_NOT_FOUND"
    assert guide_ids(session) == before


@pytest.mark.parametrize("guide_id", [0, -1])
def test_invalid_guide_id_returns_422(api, guide_id):
    client, _, _ = api
    token = login(client)

    response = client.delete(
        f"/api/my-guides/{guide_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "GUIDE_ID_INVALID"


def test_database_error_returns_500_and_preserves_data(api):
    client, session, ids = api
    token = login(client)
    before = guide_ids(session)

    with patch.object(
        DeleteOwnedGuideDAO,
        "delete_owned",
        side_effect=SQLAlchemyError("simulated database failure"),
    ):
        response = client.delete(
            f"/api/my-guides/{ids['owned_guide']}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "GUIDE_DELETE_FAILED"
    assert guide_ids(session) == before
