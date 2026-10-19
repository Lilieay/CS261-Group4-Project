from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.dao.course_dao import CourseDAO
from app.dao.delete_owned_guide_dao import DeleteOwnedGuideDAO
from app.dao.my_guide_dao import MyGuideDAO
from app.dao.update_owned_guide_dao import UpdateOwnedGuideDAO
from app.dao.user_dao import UserDAO
from app.models.guide import Guide
from app.schemas.my_guide import MyGuideDTO
from app.schemas.my_guide_update import MyGuideUpdateRequest


class MyGuideNotFound(Exception):
    pass


class MyGuideCourseNotFound(Exception):
    pass


class MyGuideStorageError(Exception):
    pass


class MyGuidesService:
    def __init__(
        self,
        session: Session,
        course_dao: CourseDAO,
        user_dao: UserDAO,
        my_guide_dao: MyGuideDAO,
        update_owned_guide_dao: UpdateOwnedGuideDAO,
        delete_owned_guide_dao: DeleteOwnedGuideDAO,
    ):
        self.session = session
        self.course_dao = course_dao
        self.user_dao = user_dao
        self.my_guide_dao = my_guide_dao
        self.update_owned_guide_dao = update_owned_guide_dao
        self.delete_owned_guide_dao = delete_owned_guide_dao

    def list_for_user(self, username: str) -> list[MyGuideDTO]:
        guides = self.my_guide_dao.list_by_username(username)
        return [self._to_dto(guide) for guide in guides]

    def update(
        self,
        guide_id: int,
        username: str,
        payload: MyGuideUpdateRequest,
    ) -> MyGuideDTO:
        try:
            owner = self.user_dao.get_by_username(username)
            if owner is None:
                raise MyGuideNotFound

            course = self.course_dao.get_by_id(payload.course_id)
            if course is None:
                raise MyGuideCourseNotFound

            guide = self.update_owned_guide_dao.update_owned(
                guide_id, owner.id, payload
            )
            if guide is None:
                raise MyGuideNotFound

            self.session.commit()
            return self._to_dto(guide)
        except SQLAlchemyError as error:
            self.session.rollback()
            raise MyGuideStorageError from error

    def delete(self, guide_id: int, username: str) -> None:
        try:
            owner = self.user_dao.get_by_username(username)
            if owner is None:
                raise MyGuideNotFound

            deleted = self.delete_owned_guide_dao.delete_owned(
                guide_id, owner.id
            )
            if not deleted:
                raise MyGuideNotFound

            self.session.commit()
        except SQLAlchemyError as error:
            self.session.rollback()
            raise MyGuideStorageError from error

    @staticmethod
    def _to_dto(guide: Guide) -> MyGuideDTO:
        return MyGuideDTO(
            id=guide.id,
            course_id=guide.course_id,
            course_code=guide.course.course_code,
            course_name=guide.course.course_name,
            instructor_name=guide.course.instructor_name,
            title=guide.title,
            academic_year=guide.academic_year,
            semester=guide.semester,
            exam_period=guide.exam_period,
            topics=guide.topics,
            exam_format=guide.exam_format,
            objective_count=guide.objective_count,
            subjective_count=guide.subjective_count,
            additional_advice=guide.additional_advice,
        )
