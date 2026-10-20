from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.dao.read_guide_dao import ReadGuideDAO
from app.dao.saved_guide_dao import SavedGuideDAO
from app.db import get_db_session
from app.routers.auth import current_user
from app.schemas.guides import GuideDetailResponseDTO
from app.services.auth import User as AuthUser
from app.services.read_guide import ReadGuideService

router = APIRouter(prefix="/api/saved-guides", tags=["Saved Guides"])


class SavedGuideState(BaseModel):
    id: int
    saved: bool


@router.get("", response_model=list[GuideDetailResponseDTO])
def list_saved_guides(
    user_context: tuple[str, AuthUser] = Depends(current_user),
    session: Session = Depends(get_db_session),
):
    try:
        return [ReadGuideService.detail(guide) for guide in
                SavedGuideDAO(session).list_by_user(user_context[1].id)]
    except SQLAlchemyError as error:
        raise HTTPException(503, "SAVED_GUIDES_UNAVAILABLE") from error


@router.get("/{guide_id}", response_model=SavedGuideState)
def saved_guide_state(
    guide_id: int = Path(gt=0, le=2147483647),
    user_context: tuple[str, AuthUser] = Depends(current_user),
    session: Session = Depends(get_db_session),
):
    try:
        return SavedGuideState(id=guide_id, saved=SavedGuideDAO(session).contains(
            user_context[1].id, guide_id
        ))
    except SQLAlchemyError as error:
        raise HTTPException(503, "SAVED_GUIDES_UNAVAILABLE") from error


@router.put("/{guide_id}", response_model=SavedGuideState)
def save_guide(
    guide_id: int = Path(gt=0, le=2147483647),
    user_context: tuple[str, AuthUser] = Depends(current_user),
    session: Session = Depends(get_db_session),
):
    user_id = user_context[1].id
    dao = SavedGuideDAO(session)
    try:
        if ReadGuideDAO(session).get_by_id(guide_id) is None:
            raise HTTPException(404, "GUIDE_NOT_FOUND")
        dao.add(user_id, guide_id)
        session.commit()
    except IntegrityError as error:
        # Two requests saving the same guide are an idempotent success.
        session.rollback()
        if not dao.contains(user_id, guide_id):
            raise HTTPException(503, "SAVED_GUIDES_UNAVAILABLE") from error
    except SQLAlchemyError as error:
        session.rollback()
        raise HTTPException(503, "SAVED_GUIDES_UNAVAILABLE") from error
    return SavedGuideState(id=guide_id, saved=True)


@router.delete("/{guide_id}", response_model=SavedGuideState)
def unsave_guide(
    guide_id: int = Path(gt=0, le=2147483647),
    user_context: tuple[str, AuthUser] = Depends(current_user),
    session: Session = Depends(get_db_session),
):
    try:
        SavedGuideDAO(session).remove(user_context[1].id, guide_id)
        session.commit()
        return SavedGuideState(id=guide_id, saved=False)
    except SQLAlchemyError as error:
        session.rollback()
        raise HTTPException(503, "SAVED_GUIDES_UNAVAILABLE") from error
