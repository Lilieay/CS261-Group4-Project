from sqlalchemy import ForeignKey, Integer, SmallInteger, String, Unicode
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Guide(Base):
    __tablename__ = "guides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"), nullable=False
    )
    publisher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Unicode(200), nullable=False)
    academic_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    semester: Mapped[int] = mapped_column(
        SmallInteger().with_variant(TINYINT(), "mssql"), nullable=False
    )
    exam_period: Mapped[str] = mapped_column(String(10), nullable=False)
    topics: Mapped[str] = mapped_column(Unicode(2000), nullable=False)
    exam_format: Mapped[str] = mapped_column(String(10), nullable=False)
    objective_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subjective_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    additional_advice: Mapped[str | None] = mapped_column(
        Unicode(2000), nullable=True
    )

    course = relationship("Course")
    publisher = relationship("User")
