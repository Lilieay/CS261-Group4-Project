import os
import subprocess
import sys
import unittest
from contextlib import ExitStack
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema

from app.db import Base, engine as application_engine
from app.models.course import Course
from app.models.course_seed_ownership import CourseSeedOwnership
from app.models.guide import Guide
from app.models.user import User
from scripts.seed_data.course_dataset import CourseDataset
from scripts.seed_data import course_seed_service
from scripts.seed_data.course_seed_service import CourseSeedService


class CourseSeedServiceTests(unittest.TestCase):
    def setUp(self):
        self.resources = ExitStack()
        self.addCleanup(self.resources.close)
        sqlserver = os.getenv("TASK26_TEST_SQLSERVER") == "1"
        self.engine = (
            create_engine(application_engine.url, connect_args={"timeout": 5})
            if sqlserver else create_engine("sqlite://")
        )
        self.resources.callback(self.engine.dispose)
        if sqlserver:
            self._configure_sqlserver()
        else:
            Base.metadata.create_all(self.engine)
            self.sessions = sessionmaker(bind=self.engine)

    def _configure_sqlserver(self):
        connection = self.resources.enter_context(self.engine.connect())
        transaction = connection.begin()
        schema = "task26_test_" + uuid4().hex

        def rollback():
            transaction.rollback()
            remaining = connection.scalar(
                text("SELECT COUNT(*) FROM sys.schemas WHERE name = :name"),
                {"name": schema},
            )
            self.assertEqual(remaining, 0, "Test schema was not rolled back")

        self.resources.callback(rollback)
        connection.execute(CreateSchema(schema))
        connection = connection.execution_options(schema_translate_map={None: schema})
        self.sessions = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
        Base.metadata.create_all(connection)

    def test_catalog_and_selectors(self):
        catalog = CourseDataset.load("demo")
        self.assertEqual(len(catalog), 24)
        self.assertEqual({e.code for e in CourseDataset.load("test")}, {"CS100", "CS101", "CS102", "CS261"})
        self.assertFalse({"CS301", "CS303", "CS403", "CS404"} & {e.code for e in catalog})
        self.assertTrue(all(1 <= len(e.instructors) <= 2 for e in catalog))
        with self.assertRaisesRegex(ValueError, "invalid"):
            CourseDataset._parse([{"code": "CS100", "name": "Course", "instructors": ["A", "B", "C"], "description": None}], "demo")
        with self.assertRaises(ValueError):
            CourseDataset.load("other")

    def test_service_import_configures_mappers_in_fresh_interpreter(self):
        backend_dir = Path(course_seed_service.__file__).resolve().parents[2]
        result = subprocess.run(
            [sys.executable, "-c", (
                "from scripts.seed_data.course_seed_service import CourseSeedService; "
                "from sqlalchemy.orm import configure_mappers; configure_mappers()"
            )],
            cwd=backend_dir,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, "fresh interpreter mapper configuration failed")

    def test_seed_is_idempotent_and_shared_restore_preserves_owner(self):
        with self.sessions.begin() as session:
            test = CourseSeedService(session, "test")
            first = test.seed()
            self.assertEqual(len(first.inserted), 4)
            self.assertEqual(len(test.seed().reused), 4)
            demo = CourseSeedService(session, "demo")
            demo.seed()
            self.assertEqual(session.scalar(select(func.count(Course.id))), 24)
            test.restore()
            self.assertEqual(len(demo.verify().reused), 24)
            report = demo.restore()
            self.assertEqual(len(report.removed), 24)
        with self.sessions() as session:
            self.assertEqual(session.scalar(select(func.count(Course.id))), 0)

    def test_shared_restore_also_works_in_reverse_order(self):
        with self.sessions.begin() as session:
            CourseSeedService(session, "test").seed()
            CourseSeedService(session, "demo").seed()
            CourseSeedService(session, "demo").restore()
            self.assertEqual(len(CourseSeedService(session, "test").verify().reused), 4)
            CourseSeedService(session, "test").restore()
        with self.sessions() as session:
            self.assertEqual(session.scalar(select(func.count(Course.id))), 0)

    def test_seed_persists_course_fields_and_ledger_between_sessions(self):
        with self.sessions.begin() as session:
            first = CourseSeedService(session, "test").seed()
            self.assertEqual(len(first.inserted), 4)
        with self.sessions() as session:
            course = session.scalar(select(Course).where(Course.course_code == "CS261"))
            receipt = session.get(CourseSeedOwnership, course.id)
            course_id = course.id
            self.assertEqual(course.instructor_name, "ผศ.ดร.ทรงศักดิ์ รองวิริยะพานิช")
            self.assertIsNotNone(course.description)
            self.assertEqual(receipt.expected_snapshot, CourseSeedService._snapshot(course))
            self.assertTrue(receipt.test_active)
        with self.sessions.begin() as session:
            report = CourseSeedService(session, "test").seed()
            self.assertEqual(len(report.reused), 4)
        with self.sessions() as session:
            self.assertEqual(session.scalar(select(Course.id).where(Course.course_code == "CS261")), course_id)

    def test_caller_rollback_clears_seed_rows_and_allows_retry(self):
        with self.assertRaisesRegex(RuntimeError, "caller abort"):
            with self.sessions.begin() as session:
                CourseSeedService(session, "test").seed()
                raise RuntimeError("caller abort")
        with self.sessions() as session:
            self.assertEqual(session.scalar(select(func.count(Course.id))), 0)
            self.assertEqual(session.scalar(select(func.count(CourseSeedOwnership.course_id))), 0)
        with self.sessions.begin() as session:
            report = CourseSeedService(session, "test").seed()
            self.assertEqual(len(report.inserted), 4)

    def test_unowned_matching_course_preserves_optional_fields(self):
        with self.sessions.begin() as session:
            entry = CourseDataset.load("test")[0]
            course = Course(course_code=entry.code, course_name=entry.name, instructor_name=entry.instructor_name, description="Keep")
            session.add(course)
        with self.sessions.begin() as session:
            report = CourseSeedService(session, "test").seed()
            self.assertNotIn("CS100", report.inserted)
            course = session.scalar(select(Course).where(Course.course_code == "CS100"))
            self.assertEqual((course.instructor_name, course.description), (entry.instructor_name, "Keep"))
            self.assertIsNone(session.get(CourseSeedOwnership, course.id))

    def test_missing_ledger_check_and_restore_are_conservative(self):
        engine = create_engine("sqlite://")
        try:
            Course.__table__.create(engine)
            Guide.__table__.create(engine)
            User.__table__.create(engine)
            sessions = sessionmaker(bind=engine)
            with sessions.begin() as session:
                session.add_all(Course(course_code=e.code, course_name=e.name, instructor_name=e.instructor_name,
                                       description=e.description) for e in CourseDataset.load("test"))
            with sessions() as session:
                CourseSeedService(session, "test").verify()
            with sessions.begin() as session:
                report = CourseSeedService(session, "test").restore()
                self.assertTrue(any(item.startswith("CS100:") for item in report.retained))
        finally:
            engine.dispose()

    def test_conflict_aborts_before_any_insert(self):
        with self.sessions.begin() as session:
            entry = CourseDataset.load("test")[0]
            session.add(Course(course_code=entry.code, course_name=entry.name, instructor_name="Different"))
        with self.assertRaisesRegex(ValueError, "conflicting instructors"):
            with self.sessions.begin() as session:
                CourseSeedService(session, "test").seed()
        with self.sessions() as session:
            self.assertEqual(session.scalar(select(func.count(Course.id))), 1)

    def test_changed_owned_course_fails_check_and_restore_keeps_claim(self):
        with self.sessions.begin() as session:
            CourseSeedService(session, "test").seed()
        with self.sessions.begin() as session:
            course = session.scalar(select(Course).where(Course.course_code == "CS100"))
            course_id = course.id
            course.course_name = "Edited"
        with self.assertRaisesRegex(ValueError, "modified"):
            with self.sessions() as session:
                CourseSeedService(session, "test").verify()
        with self.sessions.begin() as session:
            report = CourseSeedService(session, "test").restore()
            self.assertTrue(any(item.startswith("CS100:") for item in report.retained))
            self.assertTrue(session.get(CourseSeedOwnership, course_id).test_active)

    def test_guide_reference_retains_last_owned_course(self):
        with self.sessions.begin() as session:
            CourseSeedService(session, "test").seed()
            course = session.scalar(select(Course).where(Course.course_code == "CS100"))
            user = User(username="guide-owner")
            session.add(user)
            session.flush()
            session.add(Guide(course_id=course.id, publisher_id=user.id, title="Existing", academic_year=2568,
                              semester=1, exam_period="midterm", topics="Topics", exam_format="mixed"))
        with self.sessions.begin() as session:
            report = CourseSeedService(session, "test").restore()
            self.assertTrue(any(item.startswith("CS100:") for item in report.retained))
            self.assertIsNotNone(session.scalar(select(Course).where(Course.course_code == "CS100")))

    def test_restore_retry_deletes_after_guide_reference_is_removed(self):
        with self.sessions.begin() as session:
            CourseSeedService(session, "test").seed()
            course = session.scalar(select(Course).where(Course.course_code == "CS100"))
            user = User(username="retry-owner")
            session.add(user)
            session.flush()
            guide = Guide(course_id=course.id, publisher_id=user.id, title="Retry guide", academic_year=2568,
                          semester=1, exam_period="midterm", topics="Topics", exam_format="mixed")
            session.add(guide)
        with self.sessions.begin() as session:
            CourseSeedService(session, "test").restore()
            session.delete(session.scalar(select(Guide).where(Guide.title == "Retry guide")))
        with self.sessions.begin() as session:
            report = CourseSeedService(session, "test").restore()
            self.assertIn("CS100", report.removed)

    def test_modified_optional_field_retains_claim(self):
        with self.sessions.begin() as session:
            CourseSeedService(session, "test").seed()
        with self.sessions.begin() as session:
            course = session.scalar(select(Course).where(Course.course_code == "CS100"))
            course.instructor_name = "Edited instructor"
        with self.assertRaisesRegex(ValueError, "modified"):
            with self.sessions.begin() as session:
                CourseSeedService(session, "test").seed()
        with self.sessions.begin() as session:
            report = CourseSeedService(session, "test").restore()
            self.assertTrue(any(item.startswith("CS100:") for item in report.retained))

    def test_unowned_rows_conflict_on_supplied_description(self):
        entry = next(item for item in CourseDataset.load("test") if item.code == "CS261")
        with self.sessions.begin() as session:
            session.add(Course(course_code=entry.code, course_name=entry.name,
                               instructor_name=entry.instructor_name, description="Different"))
        with self.assertRaisesRegex(ValueError, "conflicting description"):
            with self.sessions.begin() as session:
                CourseSeedService(session, "test").seed()


if __name__ == "__main__":
    unittest.main()
