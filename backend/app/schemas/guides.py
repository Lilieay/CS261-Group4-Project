from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GuideListItemDTO(BaseModel):
    id: int
    title: str
    academic_year: int
    semester: Literal[1, 2, 3]
    exam_period: Literal["midterm", "final"]
    publisher_name: str


class GuideListResponseDTO(BaseModel):
    course_id: int
    has_guides: bool
    items: list[GuideListItemDTO]


class CourseInfoDTO(BaseModel):
    id: int
    course_code: str
    course_name: str
    instructor_names: str | None


class GuideDetailResponseDTO(GuideListItemDTO):
    course: CourseInfoDTO
    topics: str
    exam_format: Literal["objective", "subjective", "mixed"]
    objective_count: int | None
    subjective_count: int | None
    additional_advice: str | None


class GuideFilterOptionsResponseDTO(BaseModel):
    course_id: int
    academic_years: list[int]
    semesters: list[Literal[1, 2, 3]]
    exam_periods: list[Literal["midterm", "final"]]


class ErrorFieldDTO(BaseModel):
    field: str
    message: str


class ErrorDetailDTO(BaseModel):
    code: str
    message: str
    fields: list[ErrorFieldDTO] = Field(default_factory=list)


class ErrorResponseDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: ErrorDetailDTO
