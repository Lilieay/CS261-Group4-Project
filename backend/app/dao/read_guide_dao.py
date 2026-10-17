from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.guide import Guide


class ReadGuideDAO:
    def __init__(self, session: Session):
        self.session = session

    def list_by_course(
        self,
        course_id: int,
        academic_year: int | None = None,
        semester: int | None = None,
        exam_period: str | None = None,
    ) -> list[Guide]:
        statement = (
            select(Guide)
            .where(Guide.course_id == course_id)
            .options(joinedload(Guide.course), joinedload(Guide.publisher))
        )

        if academic_year is not None:
            statement = statement.where(Guide.academic_year == academic_year)
        if semester is not None:
            statement = statement.where(Guide.semester == semester)
        if exam_period is not None:
            statement = statement.where(Guide.exam_period == exam_period)

        return list(self.session.scalars(statement).all())

    def get_by_id(self, guide_id: int) -> Guide | None:
        statement = (
            select(Guide)
            .where(Guide.id == guide_id)
            .options(joinedload(Guide.course), joinedload(Guide.publisher))
        )
        return self.session.scalars(statement).one_or_none()

    def get_filter_values(
        self, course_id: int
    ) -> dict[str, list[int] | list[str]]:
        statement = select(
            Guide.academic_year,
            Guide.semester,
            Guide.exam_period,
        ).where(Guide.course_id == course_id)
        rows = self.session.execute(statement).all()

        return {
            "academic_years": sorted({row.academic_year for row in rows}),
            "semesters": sorted({row.semester for row in rows}),
            "exam_periods": sorted({row.exam_period for row in rows}),
        }
