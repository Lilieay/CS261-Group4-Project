from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy.orm import Session

from app.dao.course_dao import CourseDAO
from app.dao.read_guide_dao import ReadGuideDAO
from app.dependencies import get_db_session
from app.routers.auth import current_user
from app.routers.guide_errors import GuideApiRoute
from app.schemas.guides import (
    GuideDetailResponseDTO,
    GuideFilterOptionsResponseDTO,
    GuideListResponseDTO,
)
from app.services.read_guide import ReadGuideService

router = APIRouter(
    tags=["Read Guides"],
    dependencies=[Depends(current_user)],
    route_class=GuideApiRoute,
)
SessionDependency = Annotated[Session, Depends(get_db_session)]


def get_read_guide_service(session: SessionDependency) -> ReadGuideService:
    return ReadGuideService(CourseDAO(session), ReadGuideDAO(session))


ReadGuideServiceDependency = Annotated[
    ReadGuideService, Depends(get_read_guide_service)
]


def _validate_query_parameters(request: Request) -> None:
    allowed = {"academic_year", "semester", "exam_period"}
    unknown = sorted(set(request.query_params.keys()) - allowed)
    if unknown:
        raise HTTPException(status_code=422, detail="Unknown query parameters")


@router.get("/courses/{course_id}/guides", response_model=GuideListResponseDTO)
def list_guides(
    course_id: Annotated[int, Path(gt=0)],
    service: ReadGuideServiceDependency,
    request: Request,
    academic_year: Annotated[int | None, Query(ge=1, le=32767)] = None,
    semester: Annotated[int | None, Query(ge=1, le=3)] = None,
    exam_period: Annotated[Literal["midterm", "final"] | None, Query()] = None,
) -> GuideListResponseDTO:
    _validate_query_parameters(request)
    return service.list_guides(course_id, academic_year, semester, exam_period)


@router.get("/guides/{guide_id}", response_model=GuideDetailResponseDTO)
def read_guide(
    guide_id: Annotated[int, Path(gt=0)], service: ReadGuideServiceDependency
) -> GuideDetailResponseDTO:
    return service.read_guide(guide_id)


@router.get(
    "/courses/{course_id}/guides/filter-options",
    response_model=GuideFilterOptionsResponseDTO,
)
def read_filter_options(
    course_id: Annotated[int, Path(gt=0)], service: ReadGuideServiceDependency
) -> GuideFilterOptionsResponseDTO:
    return service.filter_options(course_id)
