from fastapi import APIRouter, Depends

from app.dependencies import current_user, get_my_guides_service
from app.schemas.my_guide import MyGuideDTO
from app.services.auth import AuthenticatedUser
from app.services.my_guides import MyGuidesService


router = APIRouter(prefix="/api/my-guides", tags=["My Guides"])


@router.get("", response_model=list[MyGuideDTO])
def list_my_guides(
    user_context: tuple[str, AuthenticatedUser] = Depends(current_user),
    service: MyGuidesService = Depends(get_my_guides_service),
) -> list[MyGuideDTO]:
    return service.list_for_user(user_context[1].username)
