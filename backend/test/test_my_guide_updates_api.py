from collections.abc import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db_session
from app.dao.update_owned_guide_dao import UpdateOwnedGuideDAO
from app.main import app
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User
from app.services.auth import ACTIVE_SESSIONS, User as AuthUser, create_session


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

    app.dependency_overrides[get_db_session] = override_db_session
    ACTIVE_SESSIONS.clear()
    try:
        with TestClient(app) as client:
            yield client, session, ids
    finally:
        app.dependency_overrides.clear()
        ACTIVE_SESSIONS.clear()
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def login(client: TestClient, username: str = "6800000000") -> str:
    password = "0000000000000" if username == "6800000000" else "admin123"
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
    token = create_session(AuthUser(99, "admin", "ผู้ใช้อื่น", "student"))

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
