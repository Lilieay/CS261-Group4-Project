"""Seed, verify, and conservatively restore course catalog rows."""

from dataclasses import dataclass

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.course_seed_ownership import CourseSeedOwnership
from app.models.guide import Guide
from app.models.user import User  # Register Guide.publisher's string relationship target.
from scripts.seed_data.course_dataset import CourseDataset, CourseEntry


@dataclass(frozen=True)
class SeedReport:
    inserted: tuple[str, ...] = ()
    reused: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    released: tuple[str, ...] = ()
    retained: tuple[str, ...] = ()


class CourseSeedService:
    """Operate within the caller's session and transaction."""

    def __init__(self, session: Session, dataset: str):
        if dataset not in {"test", "demo"}:
            raise ValueError("dataset must be 'test' or 'demo'")
        self.session = session
        self.dataset = dataset
        self.entries = CourseDataset.load(dataset)
        self.flag = f"{dataset}_active"

    @staticmethod
    def _snapshot(course: Course) -> dict:
        return {
            "id": course.id,
            "course_code": course.course_code,
            "course_name": course.course_name,
            "instructor_name": course.instructor_name,
            "description": course.description,
        }

    def _has_ledger(self) -> bool:
        connection = self.session.connection()
        schema_map = connection.get_execution_options().get("schema_translate_map", {})
        schema = schema_map.get(CourseSeedOwnership.__table__.schema, CourseSeedOwnership.__table__.schema)
        return inspect(connection).has_table(CourseSeedOwnership.__tablename__, schema=schema)

    def _preflight(self) -> tuple[list[CourseEntry], dict[str, Course], dict[str, CourseSeedOwnership]]:
        codes = [entry.code for entry in self.entries]
        courses = {c.course_code: c for c in self.session.scalars(
            select(Course).where(Course.course_code.in_(codes))
        )}
        ownership: dict[int, CourseSeedOwnership] = {}
        if courses and self._has_ledger():
            ownership = {o.course_id: o for o in self.session.scalars(
                select(CourseSeedOwnership).where(
                    CourseSeedOwnership.course_id.in_([c.id for c in courses.values()])
                )
            )}
        if self._has_ledger():
            for receipt in self.session.scalars(select(CourseSeedOwnership)):
                if receipt.expected_snapshot.get("course_code") not in codes:
                    continue
                owned_course = self.session.get(Course, receipt.course_id)
                if owned_course is None or self._snapshot(owned_course) != receipt.expected_snapshot:
                    raise ValueError(
                        "owned course was modified: "
                        + receipt.expected_snapshot["course_code"]
                    )
        tracked = {o.course_id: o for o in ownership.values()}
        for entry in self.entries:
            course = courses.get(entry.code)
            if course is None:
                continue
            receipt = tracked.get(course.id)
            if receipt and self._snapshot(course) != receipt.expected_snapshot:
                raise ValueError(f"owned course was modified: {entry.code}")
            if course.course_name != entry.name:
                raise ValueError(f"course code has a conflicting name: {entry.code}")
            if course.instructor_name != entry.instructor_name:
                raise ValueError(f"course code has conflicting instructors: {entry.code}")
            if entry.description is not None and course.description != entry.description:
                raise ValueError(f"course code has a conflicting description: {entry.code}")
        return list(self.entries), courses, {c.course_code: tracked[c.id] for c in courses.values() if c.id in tracked}

    def seed(self) -> SeedReport:
        entries, courses, receipts = self._preflight()
        inserted, reused = [], []
        for entry in entries:
            course = courses.get(entry.code)
            if course is None:
                course = Course(
                    course_code=entry.code,
                    course_name=entry.name,
                    instructor_name=entry.instructor_name,
                    description=entry.description,
                )
                self.session.add(course)
                self.session.flush()
                receipt = CourseSeedOwnership(course_id=course.id, expected_snapshot=self._snapshot(course))
                setattr(receipt, self.flag, True)
                self.session.add(receipt)
                inserted.append(entry.code)
            else:
                receipt = receipts.get(entry.code)
                if receipt:
                    setattr(receipt, self.flag, True)
                reused.append(entry.code)
        self.session.flush()
        return SeedReport(inserted=tuple(inserted), reused=tuple(reused))

    def verify(self) -> SeedReport:
        _, courses, receipts = self._preflight()
        missing = [e.code for e in self.entries if e.code not in courses]
        if missing:
            raise ValueError("courses are missing: " + ", ".join(missing))
        for entry in self.entries:
            receipt = receipts.get(entry.code)
            if receipt and not getattr(receipt, self.flag):
                raise ValueError(f"course is not owned by {self.dataset}: {entry.code}")
        return SeedReport(reused=tuple(e.code for e in self.entries))

    def restore(self) -> SeedReport:
        receipts = {}
        if self._has_ledger():
            receipts = {
                receipt.expected_snapshot["course_code"]: receipt
                for receipt in self.session.scalars(select(CourseSeedOwnership))
                if receipt.expected_snapshot.get("course_code") in {e.code for e in self.entries}
                and getattr(receipt, self.flag)
            }
        courses = {code: self.session.get(Course, receipt.course_id) for code, receipt in receipts.items()}
        removed, released, retained = [], [], []
        for entry in self.entries:
            course = courses.get(entry.code)
            receipt = receipts.get(entry.code)
            if receipt is None:
                if self.session.scalar(select(Course.id).where(Course.course_code == entry.code)) is not None:
                    retained.append(f"{entry.code}: unowned; preserved")
                continue
            if course is None:
                retained.append(f"{entry.code}: owned course row is missing; ledger kept")
                continue
            if self._snapshot(course) != receipt.expected_snapshot:
                retained.append(f"{entry.code}: course differs from recorded snapshot; ownership kept")
                continue
            other_owner_active = receipt.demo_active if self.dataset == "test" else receipt.test_active
            if other_owner_active:
                setattr(receipt, self.flag, False)
                released.append(entry.code)
                continue
            referenced = self.session.scalar(select(Guide.id).where(Guide.course_id == course.id).limit(1))
            if referenced is not None:
                retained.append(f"{entry.code}: referenced by a guide; ownership kept")
                continue
            self.session.delete(receipt)
            self.session.flush()
            self.session.delete(course)
            removed.append(entry.code)
        self.session.flush()
        return SeedReport(removed=tuple(removed), released=tuple(released), retained=tuple(retained))
