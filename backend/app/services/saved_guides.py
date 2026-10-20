from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.dao.read_guide_dao import ReadGuideDAO
from app.dao.saved_guide_dao import SavedGuideDAO
from app.schemas.guides import GuideDetailResponseDTO
from app.schemas.saved_guide import SavedGuideState
from app.services.read_guide import ReadGuideService


class SavedGuideNotFound(Exception):
    pass


class SavedGuideStorageError(Exception):
    pass


class SavedGuidesService:
    def __init__(
        self,
        session: Session,
        saved_guide_dao: SavedGuideDAO,
        read_guide_dao: ReadGuideDAO,
    ):
        self.session = session
        self.saved_guide_dao = saved_guide_dao
        self.read_guide_dao = read_guide_dao

    def list_for_user(self, user_id: int) -> list[GuideDetailResponseDTO]:
        try:
            return [ReadGuideService.detail(guide) for guide in
                    self.saved_guide_dao.list_by_user(user_id)]
        except SQLAlchemyError as error:
            raise SavedGuideStorageError from error

    def state(self, user_id: int, guide_id: int) -> SavedGuideState:
        try:
            return SavedGuideState(
                id=guide_id, saved=self.saved_guide_dao.contains(user_id, guide_id)
            )
        except SQLAlchemyError as error:
            raise SavedGuideStorageError from error

    def save(self, user_id: int, guide_id: int) -> SavedGuideState:
        try:
            if self.read_guide_dao.get_by_id(guide_id) is None:
                raise SavedGuideNotFound
            try:
                self.saved_guide_dao.add(user_id, guide_id)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()
                if not self.saved_guide_dao.contains(user_id, guide_id):
                    raise
        except SQLAlchemyError as error:
            self.session.rollback()
            raise SavedGuideStorageError from error
        return SavedGuideState(id=guide_id, saved=True)

    def remove(self, user_id: int, guide_id: int) -> SavedGuideState:
        try:
            self.saved_guide_dao.remove(user_id, guide_id)
            self.session.commit()
        except SQLAlchemyError as error:
            self.session.rollback()
            raise SavedGuideStorageError from error
        return SavedGuideState(id=guide_id, saved=False)
