from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dao.my_guide_dao import MyGuideDAO
from app.db import get_db_session
from app.routers.auth import current_user
from app.schemas.my_guide import MyGuideDTO
from app.services.auth import User as AuthUser


router = APIRouter(prefix="/api/my-guides", tags=["My Guides"])


@router.get("", response_model=list[MyGuideDTO])
def list_my_guides(
    user_context: tuple[str, AuthUser] = Depends(current_user),
    session: Session = Depends(get_db_session),
) -> list[MyGuideDTO]:
    authenticated_user = user_context[1]
    guides = MyGuideDAO(session).list_by_username(authenticated_user.username)
    return [
        MyGuideDTO(
            id=guide.id,
            course_id=guide.course_id,
            course_code=guide.course.course_code,
            course_name=guide.course.course_name,
            instructor_name=guide.course.instructor_name,
            title=guide.title,
            academic_year=guide.academic_year,
            semester=guide.semester,
            exam_period=guide.exam_period,
            topics=guide.topics,
            exam_format=guide.exam_format,
            objective_count=guide.objective_count,
            subjective_count=guide.subjective_count,
            additional_advice=guide.additional_advice,
        )
        for guide in guides
    ]
