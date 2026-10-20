import os
import unittest
from contextlib import ExitStack
from uuid import uuid4

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema

from app.db import Base, engine as application_engine
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User
from scripts.seed_data.guide_seed_service import GuideSeedService


class GuideSeedServiceTests(unittest.TestCase):
    def setUp(self):
        resources = ExitStack()
        self.addCleanup(resources.close)
        sqlserver = os.getenv("TASK41_TEST_SQLSERVER") == "1"
        engine = (
            create_engine(application_engine.url, connect_args={"timeout": 5})
            if sqlserver else create_engine("sqlite://")
        )
        resources.callback(engine.dispose)
        if not sqlserver:
            self.sessions = sessionmaker(bind=engine)
            Base.metadata.create_all(engine)
        else:
            self._configure_sqlserver(resources, engine)
        with self.sessions() as session, session.begin():
            session.add_all([
                Course(course_code="CS261", course_name="Software Engineering"),
                Course(course_code="CS102", course_name="Programming"),
            ])

    def _configure_sqlserver(self, resources, engine):
        connection = resources.enter_context(engine.connect())
        transaction = connection.begin()
        schema = "task41_test_" + uuid4().hex

        def rollback():
            transaction.rollback()
            remaining = connection.scalar(
                text("SELECT COUNT(*) FROM sys.schemas WHERE name = :name"),
                {"name": schema},
            )
            self.assertEqual(remaining, 0, "Test schema was not rolled back")

        resources.callback(rollback)
        connection.execute(CreateSchema(schema))
        connection = connection.execution_options(schema_translate_map={None: schema})
        self.sessions = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
        Base.metadata.create_all(connection)

    def test_seed_verify_and_restore_share_callers_transaction(self):
        with self.sessions() as session, session.begin():
            service = GuideSeedService(session, "test")
            service.seed()
            self.assertEqual(service.verify(), {"CS261": 3, "CS102": 1})
            service.seed()
            self.assertEqual(session.scalar(select(func.count(Guide.id))), 4)
            self.assertEqual(service.restore(), {"CS261": 3, "CS102": 1})
            self.assertEqual(service.restore(), {"CS261": 0, "CS102": 0})
            self.assertEqual(session.scalar(select(func.count(Guide.id))), 0)
            self.assertEqual(session.scalar(select(func.count(User.id))), 0)

    def test_seed_persists_values_between_sessions(self):
        for dataset, expected in (
            ("test", {"CS261": 3, "CS102": 1}),
            ("demo", {"CS261": 2}),
        ):
            with self.subTest(dataset=dataset):
                with self.sessions() as session, session.begin():
                    GuideSeedService(session, dataset).seed()
                with self.sessions() as session:
                    self.assertEqual(GuideSeedService(session, dataset).verify(), expected)

    def test_restore_preserves_demo_and_other_publishers_data(self):
        with self.sessions() as session, session.begin():
            test = GuideSeedService(session, "test")
            demo = GuideSeedService(session, "demo")
            test.seed()
            demo.seed()
            course = session.scalar(select(Course).where(Course.course_code == "CS261"))
            publisher = User(username="existing-user")
            session.add(publisher)
            session.flush()
            original = Guide(
                course_id=course.id, publisher_id=publisher.id,
                title="Existing guide", academic_year=2568, semester=1,
                exam_period="midterm", topics="Existing topics", exam_format="mixed",
            )
            session.add(original)
            session.flush()
            original_id = original.id
            test.restore()
            self.assertEqual(demo.verify(), {"CS261": 2})
        with self.sessions() as session:
            self.assertIsNotNone(session.get(Guide, original_id))
            self.assertEqual(session.scalar(select(func.count(Guide.id))), 3)

    def test_seed_and_restore_reject_unrelated_publisher_with_reserved_username(self):
        with self.sessions() as session, session.begin():
            session.add(User(username="t41_test_publisher", displayname_th="Existing account"))
        for action in ("seed", "restore"):
            with self.subTest(action=action):
                with self.assertRaisesRegex(ValueError, "username is already in use"):
                    with self.sessions() as session, session.begin():
                        getattr(GuideSeedService(session, "test"), action)()
        with self.sessions() as session:
            publisher = session.scalar(select(User).where(User.username == "t41_test_publisher"))
            self.assertEqual(publisher.displayname_th, "Existing account")

    def test_validation_failure_rolls_back_seed(self):
        with self.assertRaisesRegex(ValueError, "topics"):
            with self.sessions() as session, session.begin():
                service = GuideSeedService(session, "test")
                service.seed()
                guide = session.scalar(select(Guide))
                guide.topics = "Changed topics"
                session.flush()
                service.verify()
        with self.sessions() as session:
            self.assertEqual(session.scalar(select(func.count(Guide.id))), 0)
            self.assertEqual(session.scalar(select(func.count(User.id))), 0)

    def test_missing_course_leaves_no_partial_data(self):
        with self.sessions() as session, session.begin():
            course = session.scalar(select(Course).where(Course.course_code == "CS102"))
            session.delete(course)
        with self.assertRaisesRegex(ValueError, "CS102"):
            with self.sessions() as session, session.begin():
                GuideSeedService(session, "test").seed()
        with self.sessions() as session:
            self.assertEqual(session.scalar(select(func.count(Guide.id))), 0)
            self.assertEqual(session.scalar(select(func.count(User.id))), 0)


if __name__ == "__main__":
    unittest.main()
