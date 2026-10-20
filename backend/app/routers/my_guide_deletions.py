from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import current_user, get_my_guides_service
from app.schemas.my_guide_delete import MyGuideDeleteResponse
from app.services.auth import AuthenticatedUser
from app.services.my_guides import (
    MyGuideNotFound,
    MyGuidesService,
    MyGuideStorageError,
)


router = APIRouter(prefix="/api/my-guides", tags=["My Guides"])


@router.delete("/{guide_id}", response_model=MyGuideDeleteResponse)
def delete_my_guide(
    guide_id: int,
    user_context: tuple[str, AuthenticatedUser] = Depends(current_user),
    service: MyGuidesService = Depends(get_my_guides_service),
) -> MyGuideDeleteResponse:
    if guide_id <= 0:
        raise HTTPException(status_code=422, detail="GUIDE_ID_INVALID")

    try:
        service.delete(guide_id, user_context[1].username)
        return MyGuideDeleteResponse(
            id=guide_id,
            message="ลบแนวข้อสอบสำเร็จ",
        )
    except MyGuideNotFound as error:
        raise HTTPException(status_code=404, detail="GUIDE_NOT_FOUND") from error
    except MyGuideStorageError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GUIDE_DELETE_FAILED",
        ) from error
