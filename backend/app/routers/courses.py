from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.dao.course_dao import CourseDAO
from app.dependencies import get_db_session
from app.routers.auth import current_user
from app.routers.course_errors import CourseApiRoute
from app.schemas.courses import CourseDTO
from app.services.courses import CourseService

router = APIRouter(
    tags=["Courses"],
    dependencies=[Depends(current_user)],
    route_class=CourseApiRoute,
)
SessionDependency = Annotated[Session, Depends(get_db_session)]


def get_course_service(session: SessionDependency) -> CourseService:
    return CourseService(CourseDAO(session))


@router.get("/courses", response_model=list[CourseDTO])
def list_courses(
    service: Annotated[CourseService, Depends(get_course_service)],
    search: Annotated[str, Query(max_length=255)] = "",
) -> list[CourseDTO]:
    return service.search(search)


@router.get("/courses/{course_id}", response_model=CourseDTO)
def read_course(
    course_id: Annotated[int, Path(gt=0)],
    service: Annotated[CourseService, Depends(get_course_service)],
) -> CourseDTO:
    return service.get(course_id)
