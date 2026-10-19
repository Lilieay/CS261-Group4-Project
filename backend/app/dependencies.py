from collections.abc import Generator

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.auth import AuthenticatedUser, AuthService
from app.services.my_guides import MyGuidesService


bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> tuple[str, AuthenticatedUser]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="กรุณาส่ง Bearer token เพื่อยืนยันตัวตน", headers={"WWW-Authenticate": "Bearer"})
    user = auth_service.get_user(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Token ไม่ถูกต้องหรือหมดอายุ", headers={"WWW-Authenticate": "Bearer"})
    return credentials.credentials, user


def get_db_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def get_my_guides_service(
    session: Session = Depends(get_db_session),
) -> MyGuidesService:
    return MyGuidesService(session)
