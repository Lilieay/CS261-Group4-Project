from sqlalchemy import Integer, String, Unicode, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
    )
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    
    displayname_th: Mapped[str | None] = mapped_column(
        Unicode(255),
        nullable=True,
    )
    
    displayname_en: Mapped[str | None] = mapped_column(
        Unicode(255),
        nullable=True,
    )