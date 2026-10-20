"""Operational ownership receipts for reversible course seed data."""

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class CourseSeedOwnership(Base):
    __tablename__ = "course_seed_ownership"

    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id"), primary_key=True
    )
    expected_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    test_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    demo_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
