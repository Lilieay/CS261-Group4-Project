from sqlalchemy.orm import Session

from app.models.guide import Guide


class PublishGuideDAO:
    """Persist a new guide without committing the caller's transaction."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, guide: Guide) -> Guide:
        self.session.add(guide)
        self.session.flush()
        return guide
