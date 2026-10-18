from app.dao.course_dao import CourseDAO
from app.models.course import Course
from app.schemas.courses import CourseDTO


class CourseNotFound(Exception):
    pass


class CourseService:
    def __init__(self, course_dao: CourseDAO):
        self.course_dao = course_dao

    def search(self, keyword: str = "") -> list[CourseDTO]:
        return [self.to_dto(course) for course in self.course_dao.search(keyword)]

    def get(self, course_id: int) -> CourseDTO:
        course = self.course_dao.get_cs_by_id(course_id)
        if course is None:
            raise CourseNotFound
        return self.to_dto(course)

    @staticmethod
    def to_dto(course: Course) -> CourseDTO:
        return CourseDTO(
            id=course.id,
            course_code=course.course_code,
            course_name=course.course_name,
            instructor_name=course.instructor_name,
            description=course.description,
        )
