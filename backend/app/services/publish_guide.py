from sqlalchemy.orm import Session

from app.dao.course_dao import CourseDAO
from app.dao.publish_guide_dao import PublishGuideDAO
from app.dao.user_dao import UserDAO
from app.models.course import Course
from app.models.guide import Guide
from app.models.user import User
from app.schemas.guides import (
    CourseInfoDTO,
    GuideDetailResponseDTO,
    GuidePublishRequestDTO,
)
from app.services.auth import User as AuthenticatedUser


class GuidePublishNotFound(Exception):
    """Raised when a requested course is absent or outside the U4 scope."""


class PublishGuideService:
    def __init__(
        self,
        session: Session,
        course_dao: CourseDAO,
        user_dao: UserDAO,
        publish_guide_dao: PublishGuideDAO,
    ):
        self.session = session
        self.course_dao = course_dao
        self.user_dao = user_dao
        self.publish_guide_dao = publish_guide_dao

    def publish(
        self,
        payload: GuidePublishRequestDTO,
        authenticated_user: AuthenticatedUser,
    ) -> GuideDetailResponseDTO:
        course = self.course_dao.get_by_id(payload.course_id)
        if course is None or not course.course_code.strip().upper().startswith("CS"):
            raise GuidePublishNotFound("Course not found or outside U4 scope")

        try:
            publisher = self.user_dao.get_by_username(
                authenticated_user.username
            )
            if publisher is None:
                publisher = self.user_dao.get_or_create_from_tu_profile(
                    authenticated_user.username,
                    displayname_en=authenticated_user.display_name,
                )
            guide = self.publish_guide_dao.create(
                Guide(
                    course_id=course.id,
                    publisher_id=publisher.id,
                    title=payload.title,
                    academic_year=payload.academic_year,
                    semester=payload.semester,
                    exam_period=payload.exam_period,
                    topics=payload.topics,
                    exam_format=payload.exam_format,
                    objective_count=payload.objective_count,
                    subjective_count=payload.subjective_count,
                    additional_advice=payload.additional_advice,
                )
            )
            response = self._to_detail(guide, course, publisher)
            self.session.commit()
            return response
        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _to_detail(
        guide: Guide, course: Course, publisher: User
    ) -> GuideDetailResponseDTO:
        thai_name = (publisher.displayname_th or "").strip()
        english_name = (publisher.displayname_en or "").strip()
        publisher_name = (
            f"{thai_name} ({english_name})"
            if thai_name and english_name
            else thai_name or english_name or "ไม่ระบุชื่อ"
        )
        return GuideDetailResponseDTO(
            id=guide.id,
            title=guide.title,
            academic_year=guide.academic_year,
            semester=guide.semester,
            exam_period=guide.exam_period,
            publisher_name=publisher_name,
            course=CourseInfoDTO(
                id=course.id,
                course_code=course.course_code,
                course_name=course.course_name,
                instructor_names=course.instructor_name,
            ),
            topics=guide.topics,
            exam_format=guide.exam_format,
            objective_count=guide.objective_count,
            subjective_count=guide.subjective_count,
            additional_advice=guide.additional_advice,
        )
