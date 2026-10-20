from pydantic import BaseModel


class CourseDTO(BaseModel):
    id: int
    course_code: str
    course_name: str
    instructor_name: str | None = None
    description: str | None = None
