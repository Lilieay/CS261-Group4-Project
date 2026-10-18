from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db_session
from app.main import app
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User
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
    session = Session(engine)

    student = User(username="student", displayname_th="นักศึกษาทดสอบ")
    other_user = User(username="other_student", displayname_th="ผู้ใช้อื่น")
    course = Course(
        course_code="CS261",
        course_name="Software Engineering",
        instructor_name="อาจารย์ทดสอบ",
    )
    session.add_all([student, other_user, course])
    session.flush()
    session.add_all(
        [
            Guide(
                course_id=course.id,
                publisher_id=student.id,
                title="แนวข้อสอบกลางภาค",
                academic_year=2568,
                semester=1,
                exam_period="midterm",
                topics="Requirements and design",
                exam_format="mixed",
                objective_count=15,
                subjective_count=3,
                additional_advice="ทบทวนหัวข้อสำคัญ",
            ),
            Guide(
                course_id=course.id,
                publisher_id=student.id,
                title="แนวข้อสอบปลายภาค",
                academic_year=2567,
                semester=2,
                exam_period="final",
                topics="Testing",
                exam_format="subjective",
                objective_count=None,
                subjective_count=5,
                additional_advice=None,
            ),
            Guide(
                course_id=course.id,
                publisher_id=other_user.id,
                title="แนวข้อสอบของผู้ใช้อื่น",
                academic_year=2568,
                semester=1,
                exam_period="midterm",
                topics="Private to another publisher",
                exam_format="objective",
                objective_count=20,
                subjective_count=None,
            ),
        ]
    )
    session.commit()

    def override_db_session() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session

    @contextmanager
    def auth_session():
        yield session

    auth_service = AuthService(
        auth_session,
        verify=lambda username, password: (
            TUAccount(username, username, "student", True)
            if password in {"password123", "admin123"}
            else None
        ),
    )
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        session.close()
        engine.dispose()


def login(client: TestClient, username: str = "student") -> str:
    response = client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": "password123" if username == "student" else "admin123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_lists_only_authenticated_users_guides_and_expected_fields(client):
    token = login(client)

    response = client.get(
        "/api/my-guides", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    guides = response.json()
    assert [guide["title"] for guide in guides] == [
        "แนวข้อสอบกลางภาค",
        "แนวข้อสอบปลายภาค",
    ]
    assert guides[0] == {
        "id": guides[0]["id"],
        "course_id": guides[0]["course_id"],
        "course_code": "CS261",
        "course_name": "Software Engineering",
        "instructor_name": "อาจารย์ทดสอบ",
        "title": "แนวข้อสอบกลางภาค",
        "academic_year": 2568,
        "semester": 1,
        "exam_period": "midterm",
        "topics": "Requirements and design",
        "exam_format": "mixed",
        "objective_count": 15,
        "subjective_count": 3,
        "additional_advice": "ทบทวนหัวข้อสำคัญ",
    }
    assert guides[0]["id"] > 0
    assert guides[0]["course_id"] > 0
    assert all(guide["title"] != "แนวข้อสอบของผู้ใช้อื่น" for guide in guides)
    assert all("password" not in guide and "access_token" not in guide for guide in guides)


def test_requires_login_token(client):
    response = client.get("/api/my-guides")

    assert response.status_code == 401
    assert response.json()["detail"] == "กรุณาส่ง Bearer token เพื่อยืนยันตัวตน"


def test_rejects_invalid_login_token(client):
    response = client.get(
        "/api/my-guides", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token ไม่ถูกต้องหรือหมดอายุ"


def test_returns_empty_list_when_authenticated_user_has_no_guides(client):
    token = login(client, "admin")

    response = client.get(
        "/api/my-guides", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == []
