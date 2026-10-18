import os
import unittest
from contextlib import ExitStack
from uuid import uuid4

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateSchema

from app.dao.update_owned_guide_dao import UpdateOwnedGuideDAO
from app.db import Base, engine as application_engine
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User


def add_fixture_data(session: Session) -> dict[str, int]:
    owner = User(username="t69_owner", displayname_th="เจ้าของ")
    other_owner = User(username="t69_other", displayname_th="ผู้ใช้อื่น")
    old_course = Course(course_code="CS261", course_name="วิชาเดิม")
    new_course = Course(course_code="CS262", course_name="วิชาใหม่")
    session.add_all([owner, other_owner, old_course, new_course])
    session.flush()

    owned_guide = Guide(
        course_id=old_course.id,
        publisher_id=owner.id,
        title="ชื่อเดิม",
        academic_year=2567,
        semester=1,
        exam_period="midterm",
        topics="หัวข้อเดิมหนึ่ง\nหัวข้อเดิมสอง",
        exam_format="mixed",
        objective_count=10,
        subjective_count=2,
        additional_advice="คำแนะนำเดิม",
    )
    other_owned_guide = Guide(
        course_id=old_course.id,
        publisher_id=owner.id,
        title="รายการเจ้าของเดิมอีกรายการ",
        academic_year=2566,
        semester=2,
        exam_period="final",
        topics="ต้องไม่เปลี่ยน",
        exam_format="subjective",
        subjective_count=4,
    )
    guide_from_other_owner = Guide(
        course_id=old_course.id,
        publisher_id=other_owner.id,
        title="รายการของผู้ใช้อื่น",
        academic_year=2568,
        semester=1,
        exam_period="midterm",
        topics="ข้อมูลของผู้ใช้อื่น",
        exam_format="objective",
        objective_count=8,
    )
    session.add_all([owned_guide, other_owned_guide, guide_from_other_owner])
    session.flush()
    fixture_ids = {
        "owner": owner.id,
        "other_owner": other_owner.id,
        "old_course": old_course.id,
        "new_course": new_course.id,
        "owned_guide": owned_guide.id,
        "other_owned_guide": other_owned_guide.id,
        "guide_from_other_owner": guide_from_other_owner.id,
    }
    session.commit()
    return fixture_ids


class UpdateOwnedGuideDAOTests(unittest.TestCase):
    def setUp(self):
        resources = ExitStack()
        self.addCleanup(resources.close)
        sqlserver = os.getenv("TASK69_TEST_SQLSERVER") == "1"
        if sqlserver:
            engine = create_engine(
                application_engine.url, connect_args={"timeout": 5}
            )
        else:
            engine = create_engine("sqlite://", poolclass=StaticPool)
        resources.callback(engine.dispose)
        connection = resources.enter_context(engine.connect())
        transaction = connection.begin()
        schema = "task69_test_" + uuid4().hex

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
        self.ids = add_fixture_data(self.session)

    def snapshot(self, guide_id: int) -> tuple[object, ...]:
        guide = self.session.get(Guide, guide_id)
        self.assertIsNotNone(guide)
        return (
            guide.course_id,
            guide.publisher_id,
            guide.title,
            guide.academic_year,
            guide.semester,
            guide.exam_period,
            guide.topics,
            guide.exam_format,
            guide.objective_count,
            guide.subjective_count,
            guide.additional_advice,
        )

    def test_update_owned_guide_and_move_it_to_another_course(self):
        payload = {
            "course_id": self.ids["new_course"],
            "title": "ชื่อใหม่",
            "academic_year": 2568,
            "semester": 2,
            "exam_period": "final",
            "topics": "หัวข้อใหม่หนึ่ง\nหัวข้อใหม่สอง",
            "exam_format": "mixed",
            "objective_count": 12,
            "subjective_count": 3,
            "additional_advice": "คำแนะนำใหม่",
        }

        result = UpdateOwnedGuideDAO(self.session).update_owned(
            self.ids["owned_guide"], self.ids["owner"], payload
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.ids["owned_guide"])
        self.assertEqual(result.publisher_id, self.ids["owner"])
        self.assertEqual(result.course_id, self.ids["new_course"])
        self.assertEqual(result.title, "ชื่อใหม่")
        self.assertEqual(result.topics, "หัวข้อใหม่หนึ่ง\nหัวข้อใหม่สอง")
        self.assertEqual(result.objective_count, 12)
        self.assertEqual(result.subjective_count, 3)
        self.assertEqual(result.additional_advice, "คำแนะนำใหม่")
        self.assertEqual(result.course.course_code, "CS262")
        self.assertEqual(len(self.session.scalars(select(Guide)).all()), 3)
        self.assertEqual(
            self.snapshot(self.ids["other_owned_guide"])[2],
            "รายการเจ้าของเดิมอีกรายการ",
        )
        self.assertEqual(
            self.snapshot(self.ids["guide_from_other_owner"])[2],
            "รายการของผู้ใช้อื่น",
        )

    def test_non_owner_update_returns_none_and_changes_nothing(self):
        guide_id = self.ids["owned_guide"]
        before = self.snapshot(guide_id)

        result = UpdateOwnedGuideDAO(self.session).update_owned(
            guide_id,
            self.ids["other_owner"],
            {"title": "ห้ามแก้รายการของผู้อื่น"},
        )

        self.assertIsNone(result)
        self.assertEqual(self.snapshot(guide_id), before)

    def test_missing_guide_returns_none_and_changes_nothing(self):
        before_count = len(self.session.scalars(select(Guide)).all())

        result = UpdateOwnedGuideDAO(self.session).update_owned(
            99999, self.ids["owner"], {"title": "ไม่มีรายการนี้"}
        )

        self.assertIsNone(result)
        self.assertEqual(len(self.session.scalars(select(Guide)).all()), before_count)

    def test_cannot_update_owner_or_unknown_fields(self):
        guide_id = self.ids["owned_guide"]
        before = self.snapshot(guide_id)
        dao = UpdateOwnedGuideDAO(self.session)

        with self.assertRaisesRegex(ValueError, "Unsupported guide update fields"):
            dao.update_owned(
                guide_id,
                self.ids["owner"],
                {"publisher_id": self.ids["other_owner"]},
            )
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            dao.update_owned(guide_id, self.ids["owner"], {})

        self.assertEqual(self.snapshot(guide_id), before)


if __name__ == "__main__":
    unittest.main()
