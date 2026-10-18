import os
import unittest
from contextlib import ExitStack
from uuid import uuid4

from sqlalchemy import create_engine, event, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateSchema

from app.dao.publish_guide_dao import PublishGuideDAO
from app.db import Base, engine as application_engine
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User


class PublishGuideDAOTests(unittest.TestCase):
    def setUp(self):
        resources = ExitStack()
        self.addCleanup(resources.close)
        self.sqlserver = os.getenv("TASK56_TEST_SQLSERVER") == "1"
        if self.sqlserver:
            engine = create_engine(
                application_engine.url, connect_args={"timeout": 5}
            )
        else:
            engine = create_engine("sqlite://", poolclass=StaticPool)
            event.listen(engine, "connect", self._enable_sqlite_foreign_keys)
        resources.callback(engine.dispose)
        connection = resources.enter_context(engine.connect())
        transaction = connection.begin()
        schema = "task56_test_" + uuid4().hex

        def rollback_test_data():
            transaction.rollback()
            if self.sqlserver:
                remaining = connection.scalar(
                    text("SELECT COUNT(*) FROM sys.schemas WHERE name = :name"),
                    {"name": schema},
                )
                self.assertEqual(remaining, 0, "Test schema was not rolled back")

        resources.callback(rollback_test_data)
        if self.sqlserver:
            connection.execute(CreateSchema(schema))
            connection = connection.execution_options(
                schema_translate_map={None: schema}
            )
        Base.metadata.create_all(connection)
        self.session = Session(connection, join_transaction_mode="rollback_only")
        resources.callback(self.session.close)

        self.course = Course(
            course_code="CS561",
            course_name="วิชาสำหรับทดสอบการเผยแพร่",
            instructor_name="ผู้สอนทดสอบ",
        )
        self.publisher = User(
            username="task56_owner",
            displayname_th="ผู้เผยแพร่ทดสอบ",
        )
        self.session.add_all([self.course, self.publisher])
        self.session.flush()

    @staticmethod
    def _enable_sqlite_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def make_guide(self, **overrides) -> Guide:
        values = {
            "course_id": self.course.id,
            "publisher_id": self.publisher.id,
            "title": "แนวข้อสอบ Task56",
            "academic_year": 2568,
            "semester": 1,
            "exam_period": "midterm",
            "topics": "หัวข้อหนึ่ง\nหัวข้อสอง",
            "exam_format": "mixed",
            "objective_count": 20,
            "subjective_count": 3,
            "additional_advice": "ทบทวนบทเรียน",
        }
        values.update(overrides)
        return Guide(**values)

    def test_create_persists_guide_and_returns_generated_id(self):
        guide = self.make_guide()

        result = PublishGuideDAO(self.session).create(guide)

        self.assertIs(result, guide)
        self.assertGreater(result.id, 0)
        stored = self.session.get(Guide, result.id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.course_id, self.course.id)
        self.assertEqual(stored.publisher_id, self.publisher.id)
        self.assertEqual(stored.title, "แนวข้อสอบ Task56")
        self.assertEqual(stored.topics, "หัวข้อหนึ่ง\nหัวข้อสอง")
        self.assertEqual(stored.objective_count, 20)
        self.assertEqual(stored.subjective_count, 3)

    def test_create_preserves_nullable_optional_fields(self):
        guide = self.make_guide(
            objective_count=None,
            subjective_count=None,
            additional_advice=None,
        )

        result = PublishGuideDAO(self.session).create(guide)

        stored = self.session.get(Guide, result.id)
        self.assertIsNone(stored.objective_count)
        self.assertIsNone(stored.subjective_count)
        self.assertIsNone(stored.additional_advice)

    def test_create_allows_same_title_for_separate_records(self):
        dao = PublishGuideDAO(self.session)
        first = dao.create(self.make_guide())
        second = dao.create(self.make_guide(academic_year=2567))

        self.assertNotEqual(first.id, second.id)
        self.assertEqual(first.title, second.title)
        self.assertEqual(
            len(self.session.scalars(
                select(Guide).where(Guide.title == "แนวข้อสอบ Task56")
            ).all()),
            2,
        )

    def test_create_does_not_commit_callers_transaction(self):
        with self.session.begin_nested() as savepoint:
            result = PublishGuideDAO(self.session).create(self.make_guide())
            guide_id = result.id
            savepoint.rollback()

        self.assertIsNone(self.session.get(Guide, guide_id))

    def test_invalid_foreign_key_is_rejected_without_partial_record(self):
        with self.assertRaises(IntegrityError):
            with self.session.begin_nested():
                PublishGuideDAO(self.session).create(
                    self.make_guide(course_id=999999)
                )

        self.assertEqual(self.session.scalars(select(Guide)).all(), [])


if __name__ == "__main__":
    unittest.main()
