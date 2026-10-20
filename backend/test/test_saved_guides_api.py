import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db_session
from app.main import app
from app.models.course import Course
from app.models.guide import Guide
from app.models.saved_guide import SavedGuide
from app.models.user import User
from app.routers.auth import current_user
from app.services.auth import User as AuthUser


@pytest.fixture
def saved_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all([User(username="one"), User(username="two"),
                     Course(course_code="CS261", course_name="Software Engineering")])
    session.flush()
    guide = Guide(course_id=1, publisher_id=1, title="Guide", academic_year=2568,
                  semester=1, exam_period="midterm", topics="Topics", exam_format="mixed",
                  subjective_count=2, objective_count=10)
    session.add(guide)
    session.commit()
    account = {"id": 1}

    def user():
        return "test-token", AuthUser(account["id"], "one" if account["id"] == 1 else "two", "Student", "student")

    def db():
        yield session

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[current_user] = user
    app.dependency_overrides[get_db_session] = db
    try:
        with TestClient(app) as client:
            yield client, session, account
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        session.close()
        engine.dispose()


def test_saved_guides_are_persistent_idempotent_and_separate_per_user(saved_client):
    client, session, account = saved_client
    assert client.get("/api/saved-guides").json() == []
    assert client.get("/api/saved-guides/1").json() == {"id": 1, "saved": False}
    for _ in range(2):
        assert client.put("/api/saved-guides/1").json() == {"id": 1, "saved": True}
    assert len(session.scalars(select(SavedGuide)).all()) == 1
    session.expire_all()
    assert client.get("/api/saved-guides").json()[0]["title"] == "Guide"
    account["id"] = 2
    assert client.get("/api/saved-guides").json() == []
    assert client.put("/api/saved-guides/1").status_code == 200
    assert len(client.get("/api/saved-guides").json()) == 1
    assert client.delete("/api/saved-guides/1").status_code == 200
    account["id"] = 1
    assert client.get("/api/saved-guides/1").json()["saved"] is True
    for _ in range(2):
        assert client.delete("/api/saved-guides/1").json()["saved"] is False
    assert client.get("/api/saved-guides").json() == []


def test_saved_list_uses_current_content_and_guide_deletion_cascades(saved_client):
    client, session, _ = saved_client
    assert client.put("/api/saved-guides/1").status_code == 200
    guide = session.get(Guide, 1)
    guide.title = "Updated title"
    session.commit()
    assert client.get("/api/saved-guides").json()[0]["title"] == "Updated title"
    assert client.delete("/api/my-guides/1").status_code == 200
    assert client.get("/api/saved-guides").json() == []
    assert session.scalars(select(SavedGuide)).all() == []
    assert client.put("/api/saved-guides/1").status_code == 404


def test_saved_routes_require_login_and_valid_ids(saved_client):
    client, _, _ = saved_client
    assert client.put("/api/saved-guides/999").status_code == 404
    for value in ["0", "-1", "abc", "2147483648"]:
        assert client.put(f"/api/saved-guides/{value}").status_code == 422
    app.dependency_overrides.pop(current_user)
    assert client.get("/api/saved-guides").status_code == 401
    assert client.put("/api/saved-guides/1").status_code == 401
    assert client.delete("/api/saved-guides/1").status_code == 401
