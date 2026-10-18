from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.course import Course


class CourseDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, course_id: int) -> Course | None:
        statement = select(Course).where(
            Course.id == course_id
        )

        result = self.session.execute(statement)
        return result.scalar_one_or_none()

    def search(self, keyword: str = "") -> list[Course]:
        keyword = keyword.strip().lower()

        if len(keyword) > 255:
            return []

        statement = select(Course).where(Course.course_code.ilike("CS%"))

        if keyword:
            by_code = func.lower(Course.course_code).startswith(keyword)
            by_name = func.lower(Course.course_name).contains(keyword)
            statement = statement.where(or_(by_code, by_name))

        return list(self.session.scalars(statement.order_by(Course.course_code)).all())

    def get_cs_by_id(self, course_id: int) -> Course | None:
        statement = select(Course).where(
            Course.id == course_id,
            Course.course_code.ilike("CS%"),
        )
        return self.session.execute(statement).scalar_one_or_none()
