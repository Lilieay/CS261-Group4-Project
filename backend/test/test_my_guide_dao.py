import os
import unittest
from contextlib import ExitStack
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateSchema

from app.dao.my_guide_dao import MyGuideDAO
from app.db import Base, engine as application_engine
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User


def add_fixture_data(session: Session) -> tuple[User, User, list[Guide]]:
    course = Course(course_code="CS261", course_name="วิศวกรรมซอฟต์แวร์")
    other_course = Course(course_code="CS102", course_name="การเขียนโปรแกรม")
    owner = User(username="t68_owner", displayname_th="เจ้าของ")
    other_owner = User(username="t68_other", displayname_th="ผู้ใช้อื่น")
    session.add_all([course, other_course, owner, other_owner])
    session.flush()

    owned_guides = [
        Guide(
            course_id=course.id,
            publisher_id=owner.id,
            title="แนวข้อสอบกลางภาค 2568",
            academic_year=2568,
            semester=1,
            exam_period="midterm",
            topics="หัวข้อหนึ่ง\nหัวข้อสอง",
            exam_format="mixed",
            objective_count=10,
        ),
        Guide(
            course_id=other_course.id,
            publisher_id=owner.id,
            title="แนวข้อสอบปลายภาค 2567",
            academic_year=2567,
            semester=2,
            exam_period="final",
            topics="หัวข้อปลายภาค",
            exam_format="objective",
            additional_advice="อ่านบทที่ 1–3",
        ),
    ]
    guide_from_other_owner = Guide(
        course_id=course.id,
        publisher_id=other_owner.id,
        title="รายการของผู้ใช้อื่น",
        academic_year=2568,
        semester=1,
        exam_period="midterm",
        topics="ต้องไม่ปรากฏในผลลัพธ์",
        exam_format="subjective",
    )
    session.add_all([*owned_guides, guide_from_other_owner])
    session.commit()
    return owner, other_owner, owned_guides


class MyGuideDAOTests(unittest.TestCase):
    def setUp(self):
        resources = ExitStack()
        self.addCleanup(resources.close)
        sqlserver = os.getenv("TASK68_TEST_SQLSERVER") == "1"
        if sqlserver:
            engine = create_engine(
                application_engine.url, connect_args={"timeout": 5}
            )
        else:
            engine = create_engine("sqlite://", poolclass=StaticPool)
        resources.callback(engine.dispose)
        connection = resources.enter_context(engine.connect())
        transaction = connection.begin()
        schema = "task68_test_" + uuid4().hex

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

    def test_lists_only_current_username_across_courses_in_id_order(self):
        owner, other_owner, expected = add_fixture_data(self.session)

        result = MyGuideDAO(self.session).list_by_username(owner.username)

        self.assertEqual([guide.id for guide in result], [guide.id for guide in expected])
        self.assertTrue(all(guide.publisher_id == owner.id for guide in result))
        self.assertNotEqual(other_owner.id, owner.id)

    def test_returns_empty_list_for_existing_user_without_guides(self):
        user = User(username="t68_no_guides", displayname_th="ยังไม่มีรายการ")
        self.session.add(user)
        self.session.commit()

        self.assertEqual(MyGuideDAO(self.session).list_by_username(user.username), [])

    def test_returns_empty_list_for_unknown_username(self):
        add_fixture_data(self.session)

        self.assertEqual(
            MyGuideDAO(self.session).list_by_username("t68_unknown"), []
        )

    def test_course_is_eager_loaded_and_nullable_fields_are_preserved(self):
        owner, _, expected = add_fixture_data(self.session)
        username = owner.username
        expected_ids = [guide.id for guide in expected]
        self.session.expunge_all()

        result = MyGuideDAO(self.session).list_by_username(username)

        by_id = {guide.id: guide for guide in result}
        first = by_id[expected_ids[0]]
        second = by_id[expected_ids[1]]
        self.session.expunge_all()
        self.assertEqual(first.course.course_code, "CS261")
        self.assertEqual(second.course.course_code, "CS102")
        self.assertEqual(first.topics, "หัวข้อหนึ่ง\nหัวข้อสอง")
        self.assertIsNone(first.subjective_count)
        self.assertIsNone(first.additional_advice)
        self.assertEqual(second.additional_advice, "อ่านบทที่ 1–3")


if __name__ == "__main__":
    unittest.main()
