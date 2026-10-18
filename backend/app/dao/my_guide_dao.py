from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.guide import Guide
from app.models.user import User


class MyGuideDAO:
    """Read guide records published by the authenticated user."""

    def __init__(self, session: Session):
        self.session = session

    def list_by_username(self, username: str) -> list[Guide]:
        statement = (
            select(Guide)
            .join(Guide.publisher)
            .where(User.username == username)
            .options(joinedload(Guide.course))
            .order_by(Guide.id)
        )
        return list(self.session.scalars(statement).all())
