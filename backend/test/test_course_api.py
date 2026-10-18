import os
import unittest

os.environ.setdefault(
    "DB_CONNECTION_STRING",
    "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=CS261;"
    "Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes",
)
os.environ.setdefault("TU_API_MODE", "mock")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.dependencies import get_db_session
from app.main import app
from app.models.course import Course


class CourseApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(cls.engine)
        cls.session_factory = sessionmaker(bind=cls.engine)
        cls.client = TestClient(app)
        cls.previous_session_override = app.dependency_overrides.get(get_db_session)

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
            json={"username": "student", "password": "password123"},
        )
        cls.headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    @classmethod
    def tearDownClass(cls):
        if cls.previous_session_override is None:
            app.dependency_overrides.pop(get_db_session, None)
        else:
            app.dependency_overrides[get_db_session] = cls.previous_session_override
        cls.engine.dispose()

    def test_list_returns_only_cs_courses(self):
        response = self.client.get("/courses", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["course_code"] for row in response.json()], ["CS102", "CS261"])

    def test_search_matches_code_prefix_or_name(self):
        by_code = self.client.get("/courses?search=CS261", headers=self.headers)
        self.assertEqual([row["course_code"] for row in by_code.json()], ["CS261"])

        by_name = self.client.get("/courses?search=software", headers=self.headers)
        self.assertEqual([row["course_code"] for row in by_name.json()], ["CS261"])

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
