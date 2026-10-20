from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import current_user, get_my_guides_service
from app.schemas.my_guide import MyGuideDTO
from app.schemas.my_guide_update import (
    MyGuideUpdateRequest,
    MyGuideUpdateResponse,
)
from app.services.auth import AuthenticatedUser
from app.services.my_guides import (
    MyGuideCourseNotFound,
    MyGuideNotFound,
    MyGuidesService,
    MyGuideStorageError,
)


router = APIRouter(prefix="/api/my-guides", tags=["My Guides"])


@router.put("/{guide_id}", response_model=MyGuideUpdateResponse)
def update_my_guide(
    guide_id: int,
    payload: MyGuideUpdateRequest,
    user_context: tuple[str, AuthenticatedUser] = Depends(current_user),
    service: MyGuidesService = Depends(get_my_guides_service),
) -> MyGuideDTO:
    if guide_id <= 0:
        raise HTTPException(status_code=422, detail="GUIDE_ID_INVALID")

    try:
        return service.update(guide_id, user_context[1].username, payload)
    except MyGuideNotFound as error:
        raise HTTPException(status_code=404, detail="GUIDE_NOT_FOUND") from error
    except MyGuideCourseNotFound as error:
        raise HTTPException(status_code=422, detail="COURSE_NOT_FOUND") from error
    except MyGuideStorageError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GUIDE_UPDATE_FAILED",
        ) from error
