from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.guide import Guide


class DeleteOwnedGuideDAO:
    """Delete a guide only when the supplied publisher owns it."""

    def __init__(self, session: Session):
        self.session = session

    def delete_owned(self, guide_id: int, publisher_id: int) -> bool:
        statement = delete(Guide).where(
            Guide.id == guide_id,
            Guide.publisher_id == publisher_id,
        )
        result = self.session.execute(statement)
        return result.rowcount == 1
