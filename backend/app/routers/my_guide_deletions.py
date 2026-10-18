from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.dao.delete_owned_guide_dao import DeleteOwnedGuideDAO
from app.dao.user_dao import UserDAO
from app.db import get_db_session
from app.routers.auth import current_user
from app.schemas.my_guide_delete import MyGuideDeleteResponse
from app.services.auth import User as AuthUser


router = APIRouter(prefix="/api/my-guides", tags=["My Guides"])


@router.delete("/{guide_id}", response_model=MyGuideDeleteResponse)
def delete_my_guide(
    guide_id: int,
    user_context: tuple[str, AuthUser] = Depends(current_user),
    session: Session = Depends(get_db_session),
) -> MyGuideDeleteResponse:
    if guide_id <= 0:
        raise HTTPException(status_code=422, detail="GUIDE_ID_INVALID")

    try:
        authenticated_user = user_context[1]
        owner = UserDAO(session).get_by_username(authenticated_user.username)
        if owner is None:
            raise HTTPException(status_code=404, detail="GUIDE_NOT_FOUND")

        deleted = DeleteOwnedGuideDAO(session).delete_owned(guide_id, owner.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="GUIDE_NOT_FOUND")

        session.commit()
        return MyGuideDeleteResponse(
            id=guide_id,
            message="ลบแนวข้อสอบสำเร็จ",
        )
    except HTTPException:
        raise
    except SQLAlchemyError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GUIDE_DELETE_FAILED",
        ) from error
