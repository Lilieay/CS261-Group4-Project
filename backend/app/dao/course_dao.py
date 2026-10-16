from sqlalchemy import Unicode, func, literal, or_, select
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

        statement = select(Course)

        if keyword:
            term = literal(keyword, type_=Unicode())

            by_code = (
                func.charindex(
                    term,
                    func.lower(Course.course_code),
                ) == 1
            )

            by_name = (
                func.charindex(
                    term,
                    func.lower(Course.course_name),
                ) > 0
            )

            statement = statement.where(
                or_(by_code, by_name)
            )

        return list(self.session.scalars(statement).all())
        
        