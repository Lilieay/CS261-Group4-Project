import os
from contextlib import contextmanager
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema

from app.dao.course_dao import CourseDAO
from app.dao.publish_guide_dao import PublishGuideDAO
from app.dao.user_dao import UserDAO
from app.db import Base, engine as application_engine
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User
from app.schemas.guides import GuidePublishRequestDTO
from app.services.auth import AuthenticatedUser, AuthService, AuthStorageUnavailable
from app.services.publish_guide import PublishGuideService
from app.services.tu_api import TUAccount


SQLSERVER = os.getenv("USER_DAO_TEST_SQLSERVER") == "1"


@pytest.fixture
def session():
    engine = (
        create_engine(application_engine.url, connect_args={"timeout": 5})
        if SQLSERVER else create_engine("sqlite://")
    )
    if not SQLSERVER:
        @event.listens_for(engine, "connect")
        def configure_sqlite(connection, _record):
            connection.isolation_level = None

        @event.listens_for(engine, "begin")
        def begin_sqlite(connection):
            connection.exec_driver_sql("BEGIN")

    with engine.connect() as connection:
        transaction = connection.begin()
        schema = "user_transaction_test_" + uuid4().hex
        mapped = connection
        if SQLSERVER:
            connection.execute(CreateSchema(schema))
            mapped = connection.execution_options(schema_translate_map={None: schema})
        Base.metadata.create_all(mapped)
        try:
            with Session(mapped, join_transaction_mode="create_savepoint") as session:
                yield session
        finally:
            transaction.rollback()
            if SQLSERVER:
                assert connection.scalar(
                    text("SELECT COUNT(*) FROM sys.schemas WHERE name = :name"),
                    {"name": schema},
                ) == 0
    engine.dispose()


def test_new_user_and_other_pending_writes_roll_back_together(session):
    session.add(Course(course_code="CS261", course_name="Pending course"))
    user = UserDAO(session).get_or_create_from_tu_profile(
        "pending-user", displayname_en="Pending user"
    )
    assert user.id is not None

    session.rollback()

    assert session.scalar(select(func.count()).select_from(User)) == 0
    assert session.scalar(select(func.count()).select_from(Course)) == 0


def test_profile_update_is_not_committed_by_dao(session):
    user = User(username="existing-user", displayname_en="Original name")
    session.add(user)
    session.commit()

    UserDAO(session).get_or_create_from_tu_profile(
        user.username, displayname_en="Changed name"
    )
    session.rollback()

    assert session.get(User, user.id).displayname_en == "Original name"


def test_failed_publish_rolls_back_new_publisher(session):
    course = Course(course_code="CS261", course_name="Test course")
    session.add(course)
    session.commit()
    service = PublishGuideService(
        session, CourseDAO(session), UserDAO(session), PublishGuideDAO(session)
    )
    payload = GuidePublishRequestDTO(
        course_id=course.id, title="Test guide", academic_year=2568,
        semester=1, exam_period="midterm", topics="Test topics",
        exam_format="objective", objective_count=1,
    )
    with patch.object(PublishGuideDAO, "create", side_effect=SQLAlchemyError("failed")):
        with pytest.raises(SQLAlchemyError):
            service.publish(
                payload, AuthenticatedUser(999, "new-publisher", "Test user", "student")
            )

    assert session.scalar(select(func.count()).select_from(User)) == 0
    assert session.scalar(select(func.count()).select_from(Guide)) == 0


def test_failed_login_commit_rolls_back_new_user(session):
    @contextmanager
    def session_factory():
        yield session

    service = AuthService(
        session_factory,
        verify=lambda username, _password: TUAccount(username, "Test user", "student", True),
    )
    with patch.object(session, "commit", side_effect=SQLAlchemyError("failed")):
        with pytest.raises(AuthStorageUnavailable):
            service.login("new-user", "test-password")

    assert session.scalar(select(func.count()).select_from(User)) == 0


@pytest.mark.skipif(not SQLSERVER, reason="requires SQL Server duplicate-key handling")
def test_duplicate_username_recovers_without_losing_other_pending_writes(session):
    existing = User(username="existing-user", displayname_en="Original name")
    session.add(existing)
    session.commit()
    session.add(Course(course_code="CS261", course_name="Pending course"))
    dao = UserDAO(session)
    original_lookup = dao.get_by_username
    calls = 0

    def simulate_concurrent_insert(username):
        nonlocal calls
        calls += 1
        return None if calls == 1 else original_lookup(username)

    with patch.object(dao, "get_by_username", side_effect=simulate_concurrent_insert):
        user = dao.get_or_create_from_tu_profile(
            "existing-user", displayname_en="Changed name"
        )

    assert user.id == existing.id
    assert user.displayname_en == "Changed name"
    assert session.scalar(select(func.count()).select_from(Course)) == 1
    session.rollback()
    assert session.scalar(select(func.count()).select_from(Course)) == 0
    assert session.get(User, existing.id).displayname_en == "Original name"
