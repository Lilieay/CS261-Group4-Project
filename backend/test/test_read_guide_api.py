import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.dependencies import get_db_session
from app.main import app
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User
from app.routers.auth import get_auth_service
from app.services.auth import AuthService
from app.services.tu_api import TUAccount


class ReadGuideApiTests(unittest.TestCase):
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
        cls.previous_session_override = app.dependency_overrides.get(
            get_db_session
        )

        def override_session():
            with cls.session_factory() as session:
                yield session

        app.dependency_overrides[get_db_session] = override_session
        cls.previous_auth_override = app.dependency_overrides.get(get_auth_service)
        cls.auth_service = AuthService(
            cls.session_factory,
            verify=lambda username, password: (
                TUAccount(username, "Student User", "student", True)
                if password == "0000000000000"
                else None
            ),
        )
        app.dependency_overrides[get_auth_service] = lambda: cls.auth_service
        with cls.session_factory() as session:
            course = Course(
                course_code="CS261",
                course_name="Software Engineering",
                instructor_name=None,
            )
            other_course = Course(course_code="CS102", course_name="Programming")
            empty_course = Course(course_code="CS999", course_name="No guides")
            publisher = User(username="publisher", displayname_th="ผู้เผยแพร่")
            session.add_all([course, other_course, empty_course, publisher])
            session.flush()
            cls.course_id = course.id
            cls.empty_course_id = empty_course.id
            session.add_all(
                [
                    Guide(
                        course_id=course.id,
                        publisher_id=publisher.id,
                        title="กลางภาค 2568",
                        academic_year=2568,
                        semester=1,
                        exam_period="midterm",
                        topics="หัวข้อหนึ่ง\nหัวข้อสอง",
                        exam_format="mixed",
                        objective_count=20,
                        subjective_count=5,
                    ),
                    Guide(
                        course_id=course.id,
                        publisher_id=publisher.id,
                        title="ปลายภาค 2567",
                        academic_year=2567,
                        semester=2,
                        exam_period="final",
                        topics="หัวข้อสาม",
                        exam_format="subjective",
                    ),
                    Guide(
                        course_id=other_course.id,
                        publisher_id=publisher.id,
                        title="อีกวิชา",
                        academic_year=2568,
                        semester=1,
                        exam_period="midterm",
                        topics="หัวข้ออื่น",
                        exam_format="objective",
                    ),
                ]
            )
            session.commit()
            cls.guide_id = session.scalar(
                select(Guide.id).where(Guide.title == "กลางภาค 2568")
            )
        login = cls.client.post(
            "/api/auth/login",
            json={"username": "6800000000", "password": "0000000000000"},
        )
        cls.headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

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

    def test_list_requires_login_and_returns_only_requested_course(self):
        response = self.client.get(
            f"/courses/{self.course_id}/guides", headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["has_guides"])
        self.assertEqual(len(body["items"]), 2)
        self.assertTrue(
            all(item["publisher_name"] == "ผู้เผยแพร่" for item in body["items"])
        )

        unauthorized = self.client.get(f"/courses/{self.course_id}/guides")
        self.assertEqual(unauthorized.status_code, 401)
        self.assertEqual(unauthorized.json()["error"]["code"], "AUTH_REQUIRED")

    def test_list_applies_combined_filters_and_distinguishes_no_match(self):
        response = self.client.get(
            "/courses/1/guides?academic_year=2568&semester=1&exam_period=midterm",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            [item["title"] for item in response.json()["items"]],
            ["กลางภาค 2568"],
        )

        no_match = self.client.get(
            f"/courses/{self.course_id}/guides?academic_year=2500",
            headers=self.headers,
        ).json()
        self.assertTrue(no_match["has_guides"])
        self.assertEqual(no_match["items"], [])

    def test_list_rejects_invalid_and_unknown_filters(self):
        for query in ("semester=4", "academic_year=ทั้งหมด", "instructor=x"):
            with self.subTest(query=query):
                response = self.client.get(
                    f"/courses/{self.course_id}/guides?{query}",
                    headers=self.headers,
                )
                self.assertEqual(response.status_code, 422)
                self.assertEqual(
                    response.json()["error"]["code"], "INVALID_PARAMETERS"
                )

    def test_list_returns_course_not_found(self):
        response = self.client.get("/courses/999/guides", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "COURSE_NOT_FOUND")

    def test_list_for_course_without_guides_returns_empty_state(self):
        response = self.client.get(
            f"/courses/{self.empty_course_id}/guides", headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["has_guides"])
        self.assertEqual(response.json()["items"], [])

    def test_detail_returns_complete_data_with_nullable_fields(self):
        response = self.client.get(f"/guides/{self.guide_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["topics"], "หัวข้อหนึ่ง\nหัวข้อสอง")
        self.assertIsNone(body["course"]["instructor_names"])
        self.assertEqual(body["objective_count"], 20)
        self.assertIsNone(body["additional_advice"])

    def test_detail_missing_guide_returns_expected_error(self):
        response = self.client.get("/guides/999", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "GUIDE_NOT_FOUND")

    def test_filter_options_are_unique_scoped_and_empty_when_no_guides(self):
        response = self.client.get(
            f"/courses/{self.course_id}/guides/filter-options",
            headers=self.headers,
        )
        self.assertEqual(response.json()["academic_years"], [2567, 2568])
        self.assertEqual(response.json()["exam_periods"], ["final", "midterm"])

        empty_course = self.client.get(
            f"/courses/{self.empty_course_id}/guides/filter-options",
            headers=self.headers,
        )
        self.assertEqual(empty_course.status_code, 200)
        self.assertEqual(empty_course.json()["academic_years"], [])


if __name__ == "__main__":
    unittest.main()
