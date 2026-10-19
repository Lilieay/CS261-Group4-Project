"""Opt-in SQL Server checks for literal CourseDAO search behavior."""

import os
import unittest
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema

from app.dao.course_dao import CourseDAO
from app.db import Base, engine as application_engine
from app.models.course import Course


@unittest.skipUnless(os.getenv("TASK31_TEST_SQLSERVER") == "1", "requires the Task31 SQL Server test flag")
class CourseDaoSqlServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = create_engine(
            application_engine.url,
            connect_args={"timeout": 5},
        ).connect()
        cls.addClassCleanup(cls.connection.close)
        cls.transaction = cls.connection.begin()
        cls.schema = "task31_search_" + uuid4().hex
        cls.connection.execute(CreateSchema(cls.schema))
        mapped_connection = cls.connection.execution_options(
            schema_translate_map={None: cls.schema}
        )
        Base.metadata.create_all(mapped_connection, tables=[Course.__table__])
        cls.sessions = sessionmaker(
            bind=mapped_connection,
            join_transaction_mode="create_savepoint",
        )

        def rollback_schema():
            cls.transaction.rollback()
            remaining = cls.connection.scalar(
                text("SELECT COUNT(*) FROM sys.schemas WHERE name = :name"),
                {"name": cls.schema},
            )
            if remaining != 0:
                raise AssertionError("SQL Server test schema was not rolled back")

        cls.addClassCleanup(rollback_schema)

    def test_like_wildcards_and_escape_character_are_literal(self):
        rows = [
            Course(course_code="CS210%", course_name="Percent literal"),
            Course(course_code="CS210X", course_name="Percent decoy"),
            Course(course_code="CS211_", course_name="Underscore literal"),
            Course(course_code="CS211X", course_name="Underscore decoy"),
            Course(course_code="CS213", course_name="Contains percent%token"),
            Course(course_code="CS214", course_name="Contains percentXtoken"),
            Course(course_code="CS215", course_name="Contains under_score"),
            Course(course_code="CS216", course_name="Contains underXscore"),
            Course(course_code="CS217", course_name="Contains folder/%_ marker"),
            Course(course_code="CS218", course_name="Contains folder/XA marker"),
            Course(course_code="CS219%", course_name="Percent literal code"),
            Course(course_code="CS219_", course_name="Underscore literal code"),
            Course(course_code="MAT219%", course_name="Non-CS percent distractor"),
            Course(course_code="CS999", course_name="วิศวกรรมซอฟต์แวร์ขั้นสูง"),
        ]
        with self.sessions.begin() as session:
            session.add_all(rows)
            checks = {
                "CS210%": ["CS210%"],
                "CS211_": ["CS211_"],
                "percent%token": ["CS213"],
                "under_score": ["CS215"],
                "folder/%_": ["CS217"],
                "%": ["CS213", "CS217"],
                "_": ["CS215", "CS217"],
            }
            for keyword, expected in checks.items():
                with self.subTest(keyword=keyword):
                    actual = [course.course_code for course in CourseDAO(session).search(keyword)]
                    self.assertEqual(actual, expected)
            self.assertEqual(
                [course.course_code for course in CourseDAO(session).search("CS999")],
                ["CS999"],
            )
            self.assertEqual(
                [course.course_code for course in CourseDAO(session).search("วิศวกรรม")],
                ["CS999"],
            )
