import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.dependencies import get_auth_service, get_db_session
from app.main import app
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User
from app.services.auth import AuthService
from app.services.tu_api import TUAccount


class PublishGuideApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        event.listen(cls.engine, "connect", cls._enable_sqlite_foreign_keys)
        Base.metadata.create_all(cls.engine)
        cls.session_factory = sessionmaker(bind=cls.engine)
        cls.client = TestClient(app)
        cls.previous_session_override = app.dependency_overrides.get(
            get_db_session
        )
        cls.previous_auth_override = app.dependency_overrides.get(get_auth_service)

        def override_session():
            with cls.session_factory() as session:
                yield session

        app.dependency_overrides[get_db_session] = override_session
        with cls.session_factory() as session:
            session.add_all(
                [
                    Course(
                        course_code="CS261",
                        course_name="Software Engineering",
                        instructor_name="Instructor One",
                    ),
                    Course(course_code="MA111", course_name="Mathematics"),
                ]
            )
            session.commit()
            cls.cs_course_id = session.scalar(
                select(Course.id).where(Course.course_code == "CS261")
            )
            cls.non_cs_course_id = session.scalar(
                select(Course.id).where(Course.course_code == "MA111")
            )

    @classmethod
    def _enable_sqlite_foreign_keys(cls, connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    @classmethod
    def tearDownClass(cls):
        if cls.previous_session_override is None:
            app.dependency_overrides.pop(get_db_session, None)
        else:
            app.dependency_overrides[get_db_session] = cls.previous_session_override
        if cls.previous_auth_override is None:
            app.dependency_overrides.pop(get_auth_service, None)
        else:
            app.dependency_overrides[get_auth_service] = cls.previous_auth_override
        cls.engine.dispose()

    def setUp(self):
        with self.session_factory() as session:
            session.execute(Guide.__table__.delete())
            session.execute(User.__table__.delete())
            session.commit()
        self.auth_service = AuthService(
            self.session_factory,
            verify=lambda username, password: (
                TUAccount(username, "Task57 Student", "student", True)
                if password == "0000000000000"
                else None
            ),
        )
        app.dependency_overrides[get_auth_service] = lambda: self.auth_service

    def headers_for(self, username="task57_student"):
        response = self.client.post(
            "/api/auth/login",
            json={"username": username, "password": "0000000000000"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.authenticated_user_id = response.json()["user"]["id"]
        self.assertGreater(self.authenticated_user_id, 0)
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    def payload(self, **overrides):
        values = {
            "course_id": self.cs_course_id,
            "title": "แนวข้อสอบ Task57",
            "academic_year": 2569,
            "semester": 1,
            "exam_period": "midterm",
            "topics": "หัวข้อหนึ่ง\nหัวข้อสอง",
            "exam_format": "mixed",
            "objective_count": 20,
            "subjective_count": 3,
            "additional_advice": "ทบทวนเนื้อหา",
        }
        values.update(overrides)
        return values

    def test_publish_uses_authenticated_user_and_returns_created_detail(self):
        response = self.client.post(
            "/guides", json=self.payload(), headers=self.headers_for()
        )

        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertGreater(body["id"], 0)
        self.assertEqual(body["title"], "แนวข้อสอบ Task57")
        self.assertEqual(body["course"]["id"], self.cs_course_id)
        self.assertEqual(body["course"]["course_code"], "CS261")
        self.assertEqual(body["course"]["instructor_names"], "Instructor One")
        self.assertEqual(body["publisher_name"], "Task57 Student")
        with self.session_factory() as session:
            guide = session.get(Guide, body["id"])
            publisher = session.get(User, guide.publisher_id)
            self.assertEqual(publisher.username, "task57_student")
            self.assertEqual(guide.publisher_id, self.authenticated_user_id)
            self.assertEqual(publisher.id, self.authenticated_user_id)

    def test_publish_allows_nullable_optional_values_and_normalizes_advice(self):
        response = self.client.post(
            "/guides",
            json=self.payload(
                exam_format="objective",
                objective_count=10,
                subjective_count=None,
                additional_advice="   ",
            ),
            headers=self.headers_for("task57_optional"),
        )

        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertEqual(body["objective_count"], 10)
        self.assertIsNone(body["subjective_count"])
        self.assertIsNone(body["additional_advice"])

    def test_publish_requires_a_valid_login_token(self):
        missing = self.client.post("/guides", json=self.payload())
        self.assertEqual(missing.status_code, 401)
        self.assertEqual(missing.json()["error"]["code"], "AUTH_REQUIRED")

        invalid = self.client.post(
            "/guides",
            json=self.payload(),
            headers={"Authorization": "Bearer invalid-task57-token"},
        )
        self.assertEqual(invalid.status_code, 401)
        self.assertEqual(invalid.json()["error"]["code"], "AUTH_REQUIRED")

    def test_publish_rejects_missing_blank_invalid_and_spoofed_fields(self):
        missing_title = self.payload()
        missing_title.pop("title")
        cases = [
            (missing_title, "title"),
            (self.payload(title="   "), "title"),
            (self.payload(topics=" \n "), "topics"),
            (self.payload(academic_year=2500), "academic_year"),
            (self.payload(semester=4), "semester"),
            (self.payload(exam_period="quiz"), "exam_period"),
            (self.payload(objective_count=0), "objective_count"),
            (self.payload(objective_count=2.5), "objective_count"),
            (self.payload(exam_format="objective", subjective_count=2), ""),
            (self.payload(publisher_id=12345), "publisher_id"),
        ]
        headers = self.headers_for("task57_invalid")

        for payload, field in cases:
            with self.subTest(field=field, payload=payload):
                response = self.client.post("/guides", json=payload, headers=headers)
                self.assertEqual(response.status_code, 422, response.text)
                self.assertEqual(
                    response.json()["error"]["code"], "INVALID_PARAMETERS"
                )

        with self.session_factory() as session:
            self.assertEqual(session.scalar(select(func.count(Guide.id))), 0)
            self.assertEqual(session.scalar(select(func.count(User.id))), 1)
            self.assertIsNotNone(
                session.scalar(select(User).where(User.username == "task57_invalid"))
            )

    def test_publish_rejects_missing_and_out_of_scope_courses(self):
        headers = self.headers_for("task57_course_scope")
        for course_id in (999999, self.non_cs_course_id):
            with self.subTest(course_id=course_id):
                response = self.client.post(
                    "/guides",
                    json=self.payload(course_id=course_id),
                    headers=headers,
                )
                self.assertEqual(response.status_code, 404)
                self.assertEqual(
                    response.json()["error"]["code"], "COURSE_NOT_FOUND"
                )

        with self.session_factory() as session:
            self.assertEqual(session.scalar(select(func.count(Guide.id))), 0)
            persisted_user = session.scalar(
                select(User).where(User.username == "task57_course_scope")
            )
            self.assertIsNotNone(persisted_user)
            self.assertEqual(session.scalar(select(func.count(User.id))), 1)

    def test_database_failure_returns_500_and_rolls_back_guide(self):
        with patch(
            "app.services.publish_guide.PublishGuideDAO.create",
            side_effect=RuntimeError("simulated storage failure"),
        ):
            response = self.client.post(
                "/guides",
                json=self.payload(),
                headers=self.headers_for("task57_db_failure"),
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["error"]["code"], "INTERNAL_ERROR")
        with self.session_factory() as session:
            self.assertEqual(session.scalar(select(func.count(Guide.id))), 0)

    def test_publish_accepts_only_supported_academic_years(self):
        headers = self.headers_for("supported-year-user")
        for year in (2565, 2570):
            with self.subTest(year=year):
                response = self.client.post(
                    "/guides", json=self.payload(academic_year=year), headers=headers
                )
                self.assertEqual(response.status_code, 422, response.text)
        for year in (2566, 2567, 2568, 2569):
            with self.subTest(year=year):
                response = self.client.post(
                    "/guides", json=self.payload(academic_year=year), headers=headers
                )
                self.assertEqual(response.status_code, 201, response.text)
                self.assertEqual(response.json()["academic_year"], year)


if __name__ == "__main__":
    unittest.main()
