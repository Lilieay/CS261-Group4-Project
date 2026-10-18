"""Apply, verify, and restore a named guide dataset."""

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User


DATASET_DIR = Path(__file__).with_name("datasets")


class GuideSeedService:
    """Manage one dataset; the caller owns the Session and transaction."""

    def __init__(self, session: Session, dataset_name: str):
        if dataset_name not in {"test", "demo"}:
            raise ValueError("dataset_name must be 'test' or 'demo'")
        self.session = session
        self.dataset_name = dataset_name
        self.dataset = self._load_dataset(dataset_name)

    @staticmethod
    def _load_dataset(dataset_name: str) -> dict[str, Any]:
        path = DATASET_DIR / f"{dataset_name}.json"
        with path.open(encoding="utf-8") as source:
            return json.load(source)

    def seed(self) -> None:
        """Insert or refresh this dataset without committing the transaction."""
        publisher_data = self.dataset["publisher"]
        courses = self._get_required_courses()
        publisher = self._get_or_create_publisher(publisher_data)
        for item in self.dataset["guides"]:
            course = courses[item["course_code"]]
            guide = self._find_owned_guide(item, course, publisher)
            if guide is None:
                guide = Guide(course_id=course.id, publisher_id=publisher.id)
                self.session.add(guide)
            self._apply_guide_data(guide, item)
        self.session.flush()

    def verify(self) -> dict[str, int]:
        """Check all dataset fields and count matched seed rows per course."""
        publisher = self._find_publisher()
        if publisher is None:
            raise ValueError(f"Seed publisher for '{self.dataset_name}' is missing")
        courses = self._get_required_courses()
        counts: dict[str, int] = {}
        for item in self.dataset["guides"]:
            guide = self._find_owned_guide(item, courses[item["course_code"]], publisher)
            if guide is None:
                raise ValueError(f"Seed guide is missing: {item['title']}")
            for field, expected in item.items():
                if field != "course_code" and getattr(guide, field) != expected:
                    raise ValueError(f"Seed guide differs from dataset: {item['title']} ({field})")
            counts[item["course_code"]] = counts.get(item["course_code"], 0) + 1
        return counts

    def restore(self) -> dict[str, int]:
        """Remove this dataset and return actual deletion counts per course."""
        publisher = self._find_publisher()
        courses = self._get_required_courses()
        removed = dict.fromkeys(sorted(courses), 0)
        if publisher is None:
            return removed
        for item in self.dataset["guides"]:
            code = item["course_code"]
            guide = self._find_owned_guide(item, courses[code], publisher)
            if guide is not None:
                self.session.delete(guide)
                removed[code] += 1
        self.session.flush()
        referenced = self.session.scalar(
            select(Guide.id).where(Guide.publisher_id == publisher.id).limit(1)
        )
        if referenced is None:
            self.session.delete(publisher)
        self.session.flush()
        return removed

    def _get_required_courses(self) -> dict[str, Course]:
        codes = {item["course_code"] for item in self.dataset["guides"]}
        courses = {
            course.course_code: course
            for course in self.session.scalars(
                select(Course).where(Course.course_code.in_(codes))
            )
        }
        missing = codes - courses.keys()
        if missing:
            raise ValueError(
                "Required courses are missing; create them through the normal course setup first: "
                + ", ".join(sorted(missing))
            )
        return courses

    def _find_publisher(self) -> User | None:
        data = self.dataset["publisher"]
        publisher = self.session.scalar(
            select(User).where(User.username == data["username"])
        )
        if publisher is not None and any(
            getattr(publisher, field) != value for field, value in data.items()
        ):
            raise ValueError(f"Seed publisher username is already in use: {data['username']}")
        return publisher

    def _get_or_create_publisher(self, data: dict[str, Any]) -> User:
        publisher = self._find_publisher()
        if publisher is None:
            publisher = User(**data)
            self.session.add(publisher)
            self.session.flush()
        return publisher

    def _find_owned_guide(
        self, item: dict[str, Any], course: Course, publisher: User
    ) -> Guide | None:
        matches = list(self.session.scalars(
            select(Guide).where(
                Guide.course_id == course.id,
                Guide.title == item["title"],
            )
        ))
        if len(matches) > 1:
            raise ValueError(f"Duplicate seed title exists in database: {item['title']}")
        if matches and matches[0].publisher_id != publisher.id:
            raise ValueError(f"Seed title is already owned by another publisher: {item['title']}")
        return matches[0] if matches else None

    @staticmethod
    def _apply_guide_data(guide: Guide, item: dict[str, Any]) -> None:
        for field, value in item.items():
            if field != "course_code":
                setattr(guide, field, value)
