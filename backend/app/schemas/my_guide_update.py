from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.my_guide import MyGuideDTO


class MyGuideUpdateRequest(BaseModel):
    course_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    academic_year: int = Field(ge=1, le=32767)
    semester: Literal[1, 2, 3]
    exam_period: Literal["midterm", "final"]
    topics: str = Field(min_length=1, max_length=2000)
    exam_format: Literal["objective", "subjective", "mixed"]
    objective_count: int | None = Field(default=None, gt=0)
    subjective_count: int | None = Field(default=None, gt=0)
    additional_advice: str | None = Field(default=None, max_length=2000)

    @field_validator("title", "topics", mode="before")
    @classmethod
    def trim_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("ต้องไม่เว้นว่างหรือมีเฉพาะช่องว่าง")
        return value

    @field_validator("additional_advice", mode="before")
    @classmethod
    def normalize_optional_advice(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip() or None
        return value

    @model_validator(mode="after")
    def validate_count_fields(self) -> "MyGuideUpdateRequest":
        if self.exam_format == "objective" and self.subjective_count is not None:
            raise ValueError("ข้อสอบปรนัยต้องไม่มี subjective_count")
        if self.exam_format == "subjective" and self.objective_count is not None:
            raise ValueError("ข้อสอบอัตนัยต้องไม่มี objective_count")
        return self


class MyGuideUpdateResponse(MyGuideDTO):
    pass
