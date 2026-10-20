from pydantic import BaseModel


class MyGuideDTO(BaseModel):
    id: int
    course_id: int
    course_code: str
    course_name: str
    instructor_name: str | None
    title: str
    academic_year: int
    semester: int
    exam_period: str
    topics: str
    exam_format: str
    objective_count: int | None
    subjective_count: int | None
    additional_advice: str | None
