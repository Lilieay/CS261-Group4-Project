from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.dao.update_owned_guide_dao import UpdateOwnedGuideDAO
from app.db import Base
from app.dependencies import get_auth_service, get_db_session
from app.main import app
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User
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

    student = User(username="6800000000", displayname_th="นักศึกษาทดสอบ")
    other = User(username="admin", displayname_th="ผู้ใช้อื่น")
    old_course = Course(
        course_code="CS261",
        course_name="Software Engineering",
        instructor_name="อาจารย์เดิม",
    )
    new_course = Course(
        course_code="CS262",
        course_name="Database Systems",
        instructor_name="อาจารย์ใหม่",
    )
    session.add_all([student, other, old_course, new_course])
    session.flush()
    owned_guide = Guide(
        course_id=old_course.id,
        publisher_id=student.id,
        title="ชื่อเดิม",
        academic_year=2567,
        semester=1,
        exam_period="midterm",
        topics="หัวข้อเดิม",
        exam_format="mixed",
        objective_count=10,
        subjective_count=2,
        additional_advice="คำแนะนำเดิม",
    )
    other_guide = Guide(
        course_id=old_course.id,
        publisher_id=other.id,
        title="แนวข้อสอบของผู้อื่น",
        academic_year=2568,
        semester=2,
        exam_period="final",
        topics="ข้อมูลส่วนตัว",
        exam_format="subjective",
        subjective_count=5,
    )
    session.add_all([owned_guide, other_guide])
    session.commit()
    ids = {
        "owned_guide": owned_guide.id,
        "other_guide": other_guide.id,
        "student": student.id,
        "other": other.id,
        "new_course": new_course.id,
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


def valid_payload(course_id: int) -> dict[str, object]:
    return {
        "course_id": course_id,
        "title": "ชื่อที่แก้ไขแล้ว",
        "academic_year": 2568,
        "semester": 2,
        "exam_period": "final",
        "topics": "หัวข้อใหม่หนึ่ง\nหัวข้อใหม่สอง",
        "exam_format": "mixed",
        "objective_count": 12,
        "subjective_count": 3,
        "additional_advice": "ทบทวนบทที่ 1–4",
    }


def guide_snapshot(session: Session, guide_id: int) -> tuple[object, ...]:
    guide = session.get(Guide, guide_id)
    assert guide is not None
    return (
        guide.course_id,
        guide.publisher_id,
        guide.title,
        guide.academic_year,
        guide.semester,
        guide.exam_period,
        guide.topics,
        guide.exam_format,
        guide.objective_count,
        guide.subjective_count,
        guide.additional_advice,
    )


def test_owner_can_update_guide_and_move_it_to_another_course(api):
    client, session, ids = api
    before_count = len(session.scalars(select(Guide)).all())
    token = login(client)

    response = client.put(
        f"/api/my-guides/{ids['owned_guide']}",
        headers={"Authorization": f"Bearer {token}"},
        json=valid_payload(ids["new_course"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == ids["owned_guide"]
    assert body["course_id"] == ids["new_course"]
    assert body["course_code"] == "CS262"
    assert body["title"] == "ชื่อที่แก้ไขแล้ว"
    assert body["topics"] == "หัวข้อใหม่หนึ่ง\nหัวข้อใหม่สอง"
    assert body["objective_count"] == 12
    assert body["additional_advice"] == "ทบทวนบทที่ 1–4"
    updated = session.get(Guide, ids["owned_guide"])
    assert updated is not None
    assert updated.publisher_id == ids["student"]
    assert len(session.scalars(select(Guide)).all()) == before_count


def test_update_requires_login(api):
    client, _, ids = api

    response = client.put(
        f"/api/my-guides/{ids['owned_guide']}",
        json=valid_payload(ids["new_course"]),
    )

    assert response.status_code == 401


def test_update_rejects_invalid_token(api):
    client, _, ids = api

    response = client.put(
        f"/api/my-guides/{ids['owned_guide']}",
        headers={"Authorization": "Bearer invalid-token"},
        json=valid_payload(ids["new_course"]),
    )

    assert response.status_code == 401


def test_non_owner_cannot_update_another_users_guide(api):
    client, session, ids = api
    before = guide_snapshot(session, ids["owned_guide"])
    token = login(client, "admin")

    response = client.put(
        f"/api/my-guides/{ids['owned_guide']}",
        headers={"Authorization": f"Bearer {token}"},
        json=valid_payload(ids["new_course"]),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "GUIDE_NOT_FOUND"
    assert guide_snapshot(session, ids["owned_guide"]) == before


def test_missing_guide_returns_not_found(api):
    client, _, ids = api
    token = login(client)

    response = client.put(
        "/api/my-guides/99999",
        headers={"Authorization": f"Bearer {token}"},
        json=valid_payload(ids["new_course"]),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "GUIDE_NOT_FOUND"


@pytest.mark.parametrize(
    "change",
    [
        {"title": "   "},
        {"topics": "   "},
        {"objective_count": -1},
        {"course_id": 99999},
        {"semester": 4},
        {"exam_period": "quiz"},
        {"exam_format": "unknown"},
        {"exam_format": "objective", "subjective_count": 3},
    ],
    ids=[
        "blank-title",
        "blank-topics",
        "negative-count",
        "unknown-course",
        "invalid-semester",
        "invalid-exam-period",
        "invalid-format",
        "incompatible-count",
    ],
)
def test_invalid_data_returns_422_and_preserves_guide(api, change):
    client, session, ids = api
    before = guide_snapshot(session, ids["owned_guide"])
    token = login(client)
    payload = valid_payload(ids["new_course"])
    payload.update(change)

    response = client.put(
        f"/api/my-guides/{ids['owned_guide']}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )

    assert response.status_code == 422
    assert guide_snapshot(session, ids["owned_guide"]) == before


def test_database_error_returns_500_and_preserves_guide(api):
    client, session, ids = api
    before = guide_snapshot(session, ids["owned_guide"])
    token = login(client)

    with patch.object(
        UpdateOwnedGuideDAO,
        "update_owned",
        side_effect=SQLAlchemyError("simulated database failure"),
    ):
        response = client.put(
            f"/api/my-guides/{ids['owned_guide']}",
            headers={"Authorization": f"Bearer {token}"},
            json=valid_payload(ids["new_course"]),
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "GUIDE_UPDATE_FAILED"
    assert guide_snapshot(session, ids["owned_guide"]) == before


def test_update_rolls_back_changes_when_commit_fails(api):
    client, session, ids = api
    before = guide_snapshot(session, ids["owned_guide"])
    token = login(client)

    with patch.object(session, "commit", side_effect=SQLAlchemyError("commit failed")):
        response = client.put(
            f"/api/my-guides/{ids['owned_guide']}",
            headers={"Authorization": f"Bearer {token}"},
            json=valid_payload(ids["new_course"]),
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "GUIDE_UPDATE_FAILED"
    assert guide_snapshot(session, ids["owned_guide"]) == before


def test_authenticated_publish_read_update_delete_lifecycle(api):
    client, session, ids = api
    token = login(client)
    headers = {"Authorization": f"Bearer {token}"}
    original_list = client.get("/api/my-guides", headers=headers).json()
    other_guide = guide_snapshot(session, ids["other_guide"])

    created = client.post(
        "/guides", headers=headers, json=valid_payload(ids["new_course"])
    )
    assert created.status_code == 201
    guide_id = created.json()["id"]
    path = f"/api/my-guides/{guide_id}"

    listed = client.get("/api/my-guides", headers=headers)
    assert listed.status_code == 200
    assert {row["id"] for row in listed.json()} == {
        ids["owned_guide"], guide_id
    }

    old_course_id = session.get(Guide, ids["owned_guide"]).course_id
    payload = valid_payload(old_course_id)
    payload["title"] = "Updated lifecycle guide"
    updated = client.put(path, headers=headers, json=payload)
    assert updated.status_code == 200
    listed = client.get("/api/my-guides", headers=headers)
    assert next(row for row in listed.json() if row["id"] == guide_id) == updated.json()

    detail = client.get(f"/guides/{guide_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["title"] == payload["title"]
    assert detail.json()["course"]["id"] == old_course_id

    deleted = client.delete(path, headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()["id"] == guide_id
    assert client.get(f"/guides/{guide_id}", headers=headers).status_code == 404
    assert client.get("/api/my-guides", headers=headers).json() == original_list
    assert guide_snapshot(session, ids["other_guide"]) == other_guide


@pytest.mark.parametrize("year", [2566, 2567, 2568, 2569])
def test_update_accepts_supported_academic_years(api, year):
    client, _, ids = api
    token = login(client)
    payload = valid_payload(ids["new_course"])
    payload["academic_year"] = year

    response = client.put(
        f"/api/my-guides/{ids['owned_guide']}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["academic_year"] == year


@pytest.mark.parametrize("year", [2565, 2570])
def test_update_rejects_years_outside_supported_range(api, year):
    client, session, ids = api
    token = login(client)
    before = guide_snapshot(session, ids["owned_guide"])
    payload = valid_payload(ids["new_course"])
    payload["academic_year"] = year

    response = client.put(
        f"/api/my-guides/{ids['owned_guide']}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )

    assert response.status_code == 422
    assert guide_snapshot(session, ids["owned_guide"]) == before
