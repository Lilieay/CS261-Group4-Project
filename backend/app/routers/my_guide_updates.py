from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.dao.course_dao import CourseDAO
from app.dao.update_owned_guide_dao import UpdateOwnedGuideDAO
from app.dao.user_dao import UserDAO
from app.db import get_db_session
from app.routers.auth import current_user
from app.schemas.my_guide_update import (
    MyGuideUpdateRequest,
    MyGuideUpdateResponse,
)
from app.services.auth import User as AuthUser


router = APIRouter(prefix="/api/my-guides", tags=["My Guides"])


@router.put("/{guide_id}", response_model=MyGuideUpdateResponse)
def update_my_guide(
    guide_id: int,
    payload: MyGuideUpdateRequest,
    user_context: tuple[str, AuthUser] = Depends(current_user),
    session: Session = Depends(get_db_session),
) -> MyGuideUpdateResponse:
    if guide_id <= 0:
        raise HTTPException(status_code=422, detail="GUIDE_ID_INVALID")

    try:
        authenticated_user = user_context[1]
        owner = UserDAO(session).get_by_username(authenticated_user.username)
        if owner is None:
            raise HTTPException(status_code=404, detail="GUIDE_NOT_FOUND")

        course = CourseDAO(session).get_by_id(payload.course_id)
        if course is None:
            raise HTTPException(status_code=422, detail="COURSE_NOT_FOUND")

        guide = UpdateOwnedGuideDAO(session).update_owned(
            guide_id, owner.id, payload
        )
        if guide is None:
            raise HTTPException(status_code=404, detail="GUIDE_NOT_FOUND")

        session.commit()
        return MyGuideUpdateResponse(
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
    except HTTPException:
        raise
    except SQLAlchemyError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GUIDE_UPDATE_FAILED",
        ) from error
