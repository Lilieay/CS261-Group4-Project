from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy.orm import Session

from app.dao.course_dao import CourseDAO
from app.dao.publish_guide_dao import PublishGuideDAO
from app.dao.read_guide_dao import ReadGuideDAO
from app.dao.user_dao import UserDAO
from app.dependencies import current_user, get_db_session
from app.routers.guide_errors import GuideApiRoute
from app.schemas.guides import (
    GuideDetailResponseDTO,
    GuideFilterOptionsResponseDTO,
    GuideListResponseDTO,
    GuidePublishRequestDTO,
)
from app.services.auth import AuthenticatedUser
from app.services.publish_guide import PublishGuideService
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


def get_publish_guide_service(
    session: SessionDependency,
) -> PublishGuideService:
    return PublishGuideService(
        session,
        CourseDAO(session),
        UserDAO(session),
        PublishGuideDAO(session),
    )


PublishGuideServiceDependency = Annotated[
    PublishGuideService, Depends(get_publish_guide_service)
]


def _validate_query_parameters(request: Request) -> None:
    allowed = {"academic_year", "semester", "exam_period"}
    unknown = sorted(set(request.query_params.keys()) - allowed)
    if unknown:
        raise HTTPException(status_code=422, detail="Unknown query parameters")


@router.post("/guides", response_model=GuideDetailResponseDTO, status_code=201)
def publish_guide(
    payload: GuidePublishRequestDTO,
    service: PublishGuideServiceDependency,
    user_context: Annotated[
        tuple[str, AuthenticatedUser], Depends(current_user)
    ],
) -> GuideDetailResponseDTO:
    return service.publish(payload, user_context[1])


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
