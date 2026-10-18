"""Immutable course seed data loaded from the checked-in registrar extract."""

import json
import re
from dataclasses import dataclass
from pathlib import Path


DATASET_DIR = Path(__file__).with_name("datasets")
TEST_CODES = frozenset({"CS100", "CS101", "CS102", "CS261"})


@dataclass(frozen=True)
class CourseEntry:
    code: str
    name: str
    instructors: tuple[str, ...]
    description: str | None

    @property
    def instructor_name(self) -> str:
        return ", ".join(self.instructors)


class CourseDataset:
    @classmethod
    def load(cls, name: str) -> tuple[CourseEntry, ...]:
        if name not in {"test", "demo"}:
            raise ValueError("dataset must be 'test' or 'demo'")
        with (DATASET_DIR / "courses.json").open(encoding="utf-8-sig") as source:
            raw = json.load(source)
        return cls._parse(raw, name)

    @classmethod
    def _parse(cls, raw: object, name: str) -> tuple[CourseEntry, ...]:
        if not isinstance(raw, list):
            raise ValueError("course catalog must be a list")
        entries = []
        seen = set()
        for item in raw:
            if (not isinstance(item, dict) or set(item) != {"code", "name", "instructors", "description"}
                    or not isinstance(item["code"], str)
                    or not re.fullmatch(r"CS[0-9]{3}", item["code"])
                    or not isinstance(item["name"], str) or not item["name"].strip()
                    or len(item["name"]) > 255
                    or not isinstance(item["instructors"], list)
                    or not 1 <= len(item["instructors"]) <= 2
                    or any(not isinstance(person, str) or not person.strip() for person in item["instructors"])
                    or len(set(item["instructors"])) != len(item["instructors"])
                    or item["description"] is not None and not isinstance(item["description"], str)):
                raise ValueError("invalid course catalog entry")
            if item["code"] in seen:
                raise ValueError(f"duplicate course code: {item['code']}")
            seen.add(item["code"])
            entry = CourseEntry(item["code"], item["name"], tuple(item["instructors"]), item["description"])
            if len(entry.instructor_name) > 255:
                raise ValueError(f"instructor names are too long: {entry.code}")
            entries.append(entry)
        if not TEST_CODES <= seen:
            raise ValueError("course catalog is missing required test courses")
        selected = entries if name == "demo" else [e for e in entries if e.code in TEST_CODES]
        return tuple(selected)
