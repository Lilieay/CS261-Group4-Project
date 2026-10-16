from sqlalchemy import Integer, String, Unicode, UnicodeText
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

class Course(Base):
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    
    course_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )
    
    course_name: Mapped[str] = mapped_column(
        Unicode(255),
        nullable=False,
    )
    
    instructor_name: Mapped[str | None] = mapped_column(
        Unicode(255),
        nullable=True,
    )
    
    description: Mapped[str | None] = mapped_column(
        UnicodeText,
        nullable=True,
    )
    
    