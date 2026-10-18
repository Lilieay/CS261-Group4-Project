from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.auth import LoginRequest, LoginResponse, LoginStatusResponse, MessageResponse, UserDTO
from app.services.auth import User, authenticate, create_session, delete_session, get_user_by_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer(auto_error=False)


def to_user_dto(user: User) -> UserDTO:
    return UserDTO(id=user.id, username=user.username, display_name=user.display_name, role=user.role)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> tuple[str, User]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="กรุณาส่ง Bearer token เพื่อยืนยันตัวตน", headers={"WWW-Authenticate": "Bearer"})
    user = get_user_by_token(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Token ไม่ถูกต้องหรือหมดอายุ", headers={"WWW-Authenticate": "Bearer"})
    return credentials.credentials, user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง", headers={"WWW-Authenticate": "Bearer"})
    return LoginResponse(message="เข้าสู่ระบบสำเร็จ", access_token=create_session(user), user=to_user_dto(user))


@router.get("/status", response_model=LoginStatusResponse)
def login_status(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> LoginStatusResponse:
    if credentials is None or credentials.scheme.lower() != "bearer":
        return LoginStatusResponse(logged_in=False)
    user = get_user_by_token(credentials.credentials)
    return LoginStatusResponse(logged_in=user is not None, user=to_user_dto(user) if user else None)


@router.get("/me", response_model=UserDTO)
def me(user_context: tuple[str, User] = Depends(current_user)) -> UserDTO:
    return to_user_dto(user_context[1])


@router.post("/logout", response_model=MessageResponse)
def logout(user_context: tuple[str, User] = Depends(current_user)) -> MessageResponse:
    delete_session(user_context[0])
    return MessageResponse(message="ออกจากระบบสำเร็จ")

