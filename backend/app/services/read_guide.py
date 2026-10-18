from app.dao.course_dao import CourseDAO
from app.dao.read_guide_dao import ReadGuideDAO
from app.models.guide import Guide
from app.models.user import User
from app.schemas.guides import (
    CourseInfoDTO,
    GuideDetailResponseDTO,
    GuideFilterOptionsResponseDTO,
    GuideListItemDTO,
    GuideListResponseDTO,
)


class GuideReadNotFound(Exception):
    def __init__(self, code: str):
        self.code = code


class ReadGuideService:
    def __init__(self, course_dao: CourseDAO, guide_dao: ReadGuideDAO):
        self.course_dao = course_dao
        self.guide_dao = guide_dao

    def list_guides(
        self,
        course_id: int,
        academic_year: int | None,
        semester: int | None,
        exam_period: str | None,
    ) -> GuideListResponseDTO:
        self._require_course(course_id)
        filter_values = self.guide_dao.get_filter_values(course_id)
        guides = self.guide_dao.list_by_course(
            course_id, academic_year, semester, exam_period
        )
        return GuideListResponseDTO(
            course_id=course_id,
            has_guides=bool(filter_values["academic_years"]),
            items=[self._list_item(guide) for guide in guides],
        )

    def read_guide(self, guide_id: int) -> GuideDetailResponseDTO:
        guide = self.guide_dao.get_by_id(guide_id)
        if guide is None:
            raise GuideReadNotFound("GUIDE_NOT_FOUND")
        course = guide.course
        return GuideDetailResponseDTO(
            **self._list_item(guide).model_dump(),
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

    def filter_options(self, course_id: int) -> GuideFilterOptionsResponseDTO:
        self._require_course(course_id)
        values = self.guide_dao.get_filter_values(course_id)
        return GuideFilterOptionsResponseDTO(course_id=course_id, **values)

    def _require_course(self, course_id: int) -> None:
        if self.course_dao.get_by_id(course_id) is None:
            raise GuideReadNotFound("COURSE_NOT_FOUND")

    @staticmethod
    def _list_item(guide: Guide) -> GuideListItemDTO:
        return GuideListItemDTO(
            id=guide.id,
            title=guide.title,
            academic_year=guide.academic_year,
            semester=guide.semester,
            exam_period=guide.exam_period,
            publisher_name=ReadGuideService._publisher_name(guide.publisher),
        )

    @staticmethod
    def _publisher_name(publisher: User) -> str:
        thai_name = (publisher.displayname_th or "").strip()
        english_name = (publisher.displayname_en or "").strip()
        if thai_name and english_name:
            return f"{thai_name} ({english_name})"
        return thai_name or english_name or "ไม่ระบุชื่อ"
