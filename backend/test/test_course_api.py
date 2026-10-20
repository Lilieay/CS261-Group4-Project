import os
import unittest

os.environ.setdefault(
    "DB_CONNECTION_STRING",
    "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=CS261;"
    "Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes",
)
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.dependencies import get_auth_service, get_db_session
from app.main import app
from app.models.course import Course
from app.services.auth import AuthService
from app.services.tu_api import TUAccount


class CourseApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        cls.addClassCleanup(cls.engine.dispose)
        Base.metadata.create_all(cls.engine)
        cls.session_factory = sessionmaker(bind=cls.engine)
        cls.client = TestClient(app)
        cls.addClassCleanup(cls.client.close)

        def verify_test_student(username, password):
            if username == "course-test-student" and password == "course-test-password":
                return TUAccount(username, "Course API Test Student", "student", True)
            return None

        cls.auth_service = AuthService(
            cls.session_factory,
            verify=verify_test_student,
        )
        cls.previous_auth_override = app.dependency_overrides.get(get_auth_service)
        app.dependency_overrides[get_auth_service] = lambda: cls.auth_service
        cls.addClassCleanup(cls.restore_auth_override)

        cls.previous_session_override = app.dependency_overrides.get(get_db_session)

        def override_session():
            with cls.session_factory() as session:
                yield session

        app.dependency_overrides[get_db_session] = override_session
        cls.addClassCleanup(cls.restore_session_override)
        with cls.session_factory() as session:
            session.add_all(
                [
                    Course(
                        course_code="CS261",
                        course_name="Software Engineering",
                        instructor_name="อาจารย์ตัวอย่าง",
                        description="วิศวกรรมซอฟต์แวร์",
                    ),
                    Course(course_code="CS102", course_name="Programming Basics"),
                    Course(course_code="MAT101", course_name="Mathematics"),
                ]
            )
            session.commit()

        login = cls.client.post(
            "/api/auth/login",
            json={
                "username": "course-test-student",
                "password": "course-test-password",
            },
        )
        if login.status_code != 200:
            raise AssertionError(f"Test login failed: {login.status_code} {login.text}")
        cls.headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    @classmethod
    def restore_auth_override(cls):
        if cls.previous_auth_override is None:
            app.dependency_overrides.pop(get_auth_service, None)
        else:
            app.dependency_overrides[get_auth_service] = cls.previous_auth_override

    @classmethod
    def restore_session_override(cls):
        if cls.previous_session_override is None:
            app.dependency_overrides.pop(get_db_session, None)
        else:
            app.dependency_overrides[get_db_session] = cls.previous_session_override

    def test_list_returns_only_cs_courses(self):
        response = self.client.get("/courses", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["course_code"] for row in response.json()], ["CS102", "CS261"])

    def test_search_matches_code_prefix_or_name(self):
        by_code = self.client.get("/courses?search=CS261", headers=self.headers)
        self.assertEqual([row["course_code"] for row in by_code.json()], ["CS261"])

        by_name = self.client.get("/courses?search=software", headers=self.headers)
        self.assertEqual([row["course_code"] for row in by_name.json()], ["CS261"])

    def test_search_treats_like_wildcards_and_escape_character_as_literal(self):
        fixture_codes = [
            "CS210%",
            "CS210X",
            "CS211_",
            "CS211X",
            "CS212/",
            "CS213",
            "CS214",
            "CS215",
            "CS216",
            "CS217",
            "CS218",
            "CS219%",
            "CS219_",
            "MAT219%",
            "MAT219_",
        ]
        with self.session_factory() as session:
            session.add_all(
                [
                    Course(course_code="CS210%", course_name="Percent code % token"),
                    Course(course_code="CS210X", course_name="Percent decoy"),
                    Course(course_code="CS211_", course_name="Underscore code _ token"),
                    Course(course_code="CS211X", course_name="Underscore decoy"),
                    Course(course_code="CS212/", course_name="Slash code"),
                    Course(course_code="CS213", course_name="Contains percent%token"),
                    Course(course_code="CS214", course_name="Contains percentXtoken"),
                    Course(course_code="CS215", course_name="Contains under_score"),
                    Course(course_code="CS216", course_name="Contains underXscore"),
                    Course(course_code="CS217", course_name="Contains folder/%_ marker"),
                    Course(course_code="CS218", course_name="Contains folder/XA marker"),
                    Course(course_code="CS219%", course_name="Percent literal % code"),
                    Course(course_code="CS219_", course_name="Underscore literal _ code"),
                    Course(course_code="MAT219%", course_name="Non-CS % distractor"),
                    Course(course_code="MAT219_", course_name="Non-CS _ distractor"),
                ]
            )
            session.commit()

        try:
            for term, expected in (
                ("CS210%", ["CS210%"]),
                ("CS211_", ["CS211_"]),
                ("CS212/", ["CS212/"]),
                ("percent%token", ["CS213"]),
                ("under_score", ["CS215"]),
                ("folder/%_", ["CS217"]),
                ("%", ["CS210%", "CS213", "CS217", "CS219%"]),
                ("_", ["CS211_", "CS215", "CS217", "CS219_"]),
            ):
                with self.subTest(term=term):
                    response = self.client.get(
                        "/courses",
                        params={"search": term},
                        headers=self.headers,
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        [row["course_code"] for row in response.json()],
                        expected,
                    )
        finally:
            with self.session_factory() as session:
                session.query(Course).filter(
                    Course.course_code.in_(fixture_codes)
                ).delete(synchronize_session=False)
                session.commit()

    def test_detail_returns_course_dto(self):
        response = self.client.get("/courses/1", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "id": 1,
                "course_code": "CS261",
                "course_name": "Software Engineering",
                "instructor_name": "อาจารย์ตัวอย่าง",
                "description": "วิศวกรรมซอฟต์แวร์",
            },
        )

    def test_detail_rejects_missing_course(self):
        response = self.client.get("/courses/999", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "COURSE_NOT_FOUND")

    def test_course_api_requires_existing_login(self):
        response = self.client.get("/courses")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "AUTH_REQUIRED")


if __name__ == "__main__":
    unittest.main()
