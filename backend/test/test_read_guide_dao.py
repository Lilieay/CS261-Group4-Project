import os
import unittest
from contextlib import ExitStack
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateSchema

from app.dao.read_guide_dao import ReadGuideDAO
from app.db import Base, engine as application_engine
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User


def add_fixture_data(session: Session) -> tuple[Course, Course, Guide, Guide, Guide]:
    course = Course(course_code="CS261", course_name="Software Engineering")
    other_course = Course(course_code="CS102", course_name="Programming")
    publisher = User(username="publisher", displayname_th="ผู้เผยแพร่")
    session.add_all([course, other_course, publisher])
    session.flush()

    first = Guide(
        course_id=course.id,
        publisher_id=publisher.id,
        title="แนวข้อสอบกลางภาค 2568",
        academic_year=2568,
        semester=1,
        exam_period="midterm",
        topics="หัวข้อที่หนึ่ง\nหัวข้อที่สอง",
        exam_format="mixed",
    )
    second = Guide(
        course_id=course.id,
        publisher_id=publisher.id,
        title="Final 2567",
        academic_year=2567,
        semester=2,
        exam_period="final",
        topics="Topic B",
        exam_format="objective",
    )
    other = Guide(
        course_id=other_course.id,
        publisher_id=publisher.id,
        title="Other course",
        academic_year=2568,
        semester=1,
        exam_period="midterm",
        topics="Topic C",
        exam_format="subjective",
    )
    session.add_all([first, second, other])
    session.commit()
    return course, other_course, first, second, other


class ReadGuideDAOTests(unittest.TestCase):
    def setUp(self):
        resources = ExitStack()
        self.addCleanup(resources.close)
        sqlserver = os.getenv("TASK40_TEST_SQLSERVER") == "1"
        if sqlserver:
            engine = create_engine(
                application_engine.url, connect_args={"timeout": 5}
            )
        else:
            engine = create_engine("sqlite://", poolclass=StaticPool)
        resources.callback(engine.dispose)
        connection = resources.enter_context(engine.connect())
        transaction = connection.begin()
        schema = "task40_test_" + uuid4().hex

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

    def test_list_by_course_combines_filters_and_eager_loads_relations(self):
        course, _, first, _, _ = add_fixture_data(self.session)

        result = ReadGuideDAO(self.session).list_by_course(
            course.id,
            academic_year=2568,
            semester=1,
            exam_period="midterm",
        )

        self.assertEqual([guide.id for guide in result], [first.id])
        self.session.expunge_all()
        self.assertEqual(result[0].course.course_code, "CS261")
        self.assertEqual(result[0].publisher.displayname_th, "ผู้เผยแพร่")

    def test_list_by_course_filters_individually_and_without_filters(self):
        course, _, first, second, _ = add_fixture_data(self.session)
        dao = ReadGuideDAO(self.session)

        self.assertEqual(
            {guide.id for guide in dao.list_by_course(course.id)},
            {first.id, second.id},
        )
        for filters in (
            {"academic_year": 2568},
            {"semester": 1},
            {"exam_period": "midterm"},
        ):
            with self.subTest(filters=filters):
                self.assertEqual(
                    [guide.id for guide in dao.list_by_course(course.id, **filters)],
                    [first.id],
                )

    def test_list_by_course_without_matches_returns_empty_list(self):
        course, _, *_ = add_fixture_data(self.session)

        result = ReadGuideDAO(self.session).list_by_course(
            course.id, academic_year=2500
        )

        self.assertEqual(result, [])

    def test_list_by_course_never_returns_another_course(self):
        course, other_course, _, _, other = add_fixture_data(self.session)

        result = ReadGuideDAO(self.session).list_by_course(
            course.id, academic_year=other.academic_year
        )

        self.assertTrue(all(guide.course_id == course.id for guide in result))
        self.assertNotEqual(other_course.id, course.id)

    def test_get_by_id_returns_relations_or_none(self):
        _, _, first, _, _ = add_fixture_data(self.session)
        dao = ReadGuideDAO(self.session)

        result = dao.get_by_id(first.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.title, "แนวข้อสอบกลางภาค 2568")
        self.assertEqual(result.topics, "หัวข้อที่หนึ่ง\nหัวข้อที่สอง")
        self.assertIsNone(result.objective_count)
        self.assertIsNone(result.subjective_count)
        self.assertIsNone(result.additional_advice)
        self.assertEqual(result.course.course_code, "CS261")
        self.assertEqual(result.publisher.username, "publisher")
        self.assertIsNone(dao.get_by_id(-1))

    def test_filter_values_are_distinct_sorted_and_scoped_to_course(self):
        course, other_course, *_ = add_fixture_data(self.session)
        first = ReadGuideDAO(self.session).list_by_course(course.id)[0]
        self.session.add(Guide(
            course_id=course.id,
            publisher_id=first.publisher_id,
            title="Duplicate filter values",
            academic_year=first.academic_year,
            semester=first.semester,
            exam_period=first.exam_period,
            topics="Another guide with the same filters",
            exam_format="mixed",
        ))
        self.session.commit()
        dao = ReadGuideDAO(self.session)

        self.assertEqual(dao.get_filter_values(course.id), {
            "academic_years": [2567, 2568],
            "semesters": [1, 2],
            "exam_periods": ["final", "midterm"],
        })
        self.assertEqual(dao.get_filter_values(other_course.id), {
            "academic_years": [2568],
            "semesters": [1],
            "exam_periods": ["midterm"],
        })

    def test_filter_values_for_course_without_guides_are_empty(self):
        course = Course(course_code="CS999", course_name="No guides")
        self.session.add(course)
        self.session.commit()

        self.assertEqual(ReadGuideDAO(self.session).get_filter_values(course.id), {
            "academic_years": [],
            "semesters": [],
            "exam_periods": [],
        })


if __name__ == "__main__":
    unittest.main()
