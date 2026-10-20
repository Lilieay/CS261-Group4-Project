from fastapi import APIRouter, Depends, HTTPException, Path

from app.dependencies import current_user, get_saved_guides_service
from app.schemas.guides import GuideDetailResponseDTO
from app.schemas.saved_guide import SavedGuideState
from app.services.auth import AuthenticatedUser
from app.services.saved_guides import (
    SavedGuideNotFound,
    SavedGuidesService,
    SavedGuideStorageError,
)

router = APIRouter(prefix="/api/saved-guides", tags=["Saved Guides"])


@router.get("", response_model=list[GuideDetailResponseDTO])
def list_saved_guides(
    user_context: tuple[str, AuthenticatedUser] = Depends(current_user),
    service: SavedGuidesService = Depends(get_saved_guides_service),
):
    try:
        return service.list_for_user(user_context[1].id)
    except SavedGuideStorageError as error:
        raise HTTPException(503, "SAVED_GUIDES_UNAVAILABLE") from error


@router.get("/{guide_id}", response_model=SavedGuideState)
def saved_guide_state(
    guide_id: int = Path(gt=0, le=2147483647),
    user_context: tuple[str, AuthenticatedUser] = Depends(current_user),
    service: SavedGuidesService = Depends(get_saved_guides_service),
):
    try:
        return service.state(user_context[1].id, guide_id)
    except SavedGuideStorageError as error:
        raise HTTPException(503, "SAVED_GUIDES_UNAVAILABLE") from error


@router.put("/{guide_id}", response_model=SavedGuideState)
def save_guide(
    guide_id: int = Path(gt=0, le=2147483647),
    user_context: tuple[str, AuthenticatedUser] = Depends(current_user),
    service: SavedGuidesService = Depends(get_saved_guides_service),
):
    try:
        return service.save(user_context[1].id, guide_id)
    except SavedGuideNotFound as error:
        raise HTTPException(404, "GUIDE_NOT_FOUND") from error
    except SavedGuideStorageError as error:
        raise HTTPException(503, "SAVED_GUIDES_UNAVAILABLE") from error


@router.delete("/{guide_id}", response_model=SavedGuideState)
def unsave_guide(
    guide_id: int = Path(gt=0, le=2147483647),
    user_context: tuple[str, AuthenticatedUser] = Depends(current_user),
    service: SavedGuidesService = Depends(get_saved_guides_service),
):
    try:
        return service.remove(user_context[1].id, guide_id)
    except SavedGuideStorageError as error:
        raise HTTPException(503, "SAVED_GUIDES_UNAVAILABLE") from error
