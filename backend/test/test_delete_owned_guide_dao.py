import os
import unittest
from contextlib import ExitStack
from uuid import uuid4

if os.getenv("TASK70_TEST_SQLSERVER") != "1":
    os.environ.setdefault(
        "DB_CONNECTION_STRING",
        "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;"
        "DATABASE=CS261Group4Dev;Trusted_Connection=yes;",
    )

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateSchema

from app.dao.delete_owned_guide_dao import DeleteOwnedGuideDAO
from app.db import Base, engine as application_engine
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User


class DeleteOwnedGuideDAOTests(unittest.TestCase):
    def setUp(self):
        resources = ExitStack()
        self.addCleanup(resources.close)
        sqlserver = os.getenv("TASK70_TEST_SQLSERVER") == "1"
        if sqlserver:
            engine = create_engine(
                application_engine.url, connect_args={"timeout": 5}
            )
        else:
            engine = create_engine("sqlite://", poolclass=StaticPool)
        resources.callback(engine.dispose)
        connection = resources.enter_context(engine.connect())
        transaction = connection.begin()
        schema = "task70_test_" + uuid4().hex

        def rollback():
            transaction.rollback()
            if sqlserver:
                remaining = connection.scalar(
                    text("SELECT COUNT(*) FROM sys.schemas WHERE name = :name"),
                    {"name": schema},
                )
                self.assertEqual(remaining, 0, "Test schema was not rolled back")

        resources.callback(rollback)
        if sqlserver:
            connection.execute(CreateSchema(schema))
            connection = connection.execution_options(
                schema_translate_map={None: schema}
            )
        Base.metadata.create_all(connection)
        self.session = Session(connection, join_transaction_mode="rollback_only")
        resources.callback(self.session.close)

        course = Course(course_code="CS261", course_name="Software Engineering")
        owner = User(username="task70_owner", displayname_th="เจ้าของ")
        other_user = User(username="task70_other", displayname_th="ผู้ใช้อื่น")
        self.session.add_all([course, owner, other_user])
        self.session.flush()
        owned = Guide(
            course_id=course.id,
            publisher_id=owner.id,
            title="แนวข้อสอบของเจ้าของ",
            academic_year=2568,
            semester=1,
            exam_period="midterm",
            topics="ข้อมูลทดสอบ",
            exam_format="mixed",
        )
        self.other_owned = Guide(
            course_id=course.id,
            publisher_id=owner.id,
            title="แนวข้อสอบอีกชุด",
            academic_year=2567,
            semester=2,
            exam_period="final",
            topics="ต้องคงอยู่",
            exam_format="objective",
        )
        self.not_owned = Guide(
            course_id=course.id,
            publisher_id=other_user.id,
            title="แนวข้อสอบของผู้ใช้อื่น",
            academic_year=2568,
            semester=1,
            exam_period="midterm",
            topics="ต้องคงอยู่",
            exam_format="subjective",
        )
        self.session.add_all([owned, self.other_owned, self.not_owned])
        self.session.flush()
        self.owned_id = owned.id
        self.owner_id = owner.id
        self.other_owned_id = self.other_owned.id
        self.not_owned_id = self.not_owned.id

    def _existing_ids(self) -> set[int]:
        return set(self.session.scalars(select(Guide.id)).all())

    def test_deletes_guide_when_publisher_owns_it(self):
        deleted = DeleteOwnedGuideDAO(self.session).delete_owned(
            self.owned_id, self.owner_id
        )

        self.assertTrue(deleted)
        self.assertEqual(
            self._existing_ids(), {self.other_owned_id, self.not_owned_id}
        )

    def test_does_not_delete_guide_owned_by_another_publisher(self):
        deleted = DeleteOwnedGuideDAO(self.session).delete_owned(
            self.not_owned_id, self.owner_id
        )

        self.assertFalse(deleted)
        self.assertEqual(
            self._existing_ids(),
            {self.owned_id, self.other_owned_id, self.not_owned_id},
        )

    def test_returns_false_when_guide_does_not_exist(self):
        deleted = DeleteOwnedGuideDAO(self.session).delete_owned(-1, self.owner_id)

        self.assertFalse(deleted)
        self.assertEqual(
            self._existing_ids(),
            {self.owned_id, self.other_owned_id, self.not_owned_id},
        )

    def test_deleting_one_owned_guide_preserves_other_guides(self):
        dao = DeleteOwnedGuideDAO(self.session)

        self.assertTrue(dao.delete_owned(self.owned_id, self.owner_id))
        self.assertEqual(self._existing_ids(), {self.other_owned_id, self.not_owned_id})

    def test_same_guide_cannot_be_deleted_twice(self):
        dao = DeleteOwnedGuideDAO(self.session)

        self.assertTrue(dao.delete_owned(self.owned_id, self.owner_id))
        self.assertFalse(dao.delete_owned(self.owned_id, self.owner_id))


if __name__ == "__main__":
    unittest.main()
