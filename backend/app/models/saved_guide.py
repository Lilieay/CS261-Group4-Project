from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SavedGuide(Base):
    __tablename__ = "saved_guides"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )
    guide_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("guides.id", ondelete="CASCADE"), primary_key=True
    )
