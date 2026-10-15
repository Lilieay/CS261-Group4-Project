from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import bearer_scheme, require_login
from app.schemas.auth import LoginRequest, LoginResponse, LoginStatusResponse, MessageResponse, UserDTO
from app.services.auth import User, authenticate, create_session, delete_session, get_user_by_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def to_user_dto(user: User) -> UserDTO:
    return UserDTO(id=user.id, username=user.username, display_name=user.display_name, role=user.role)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", headers={"WWW-Authenticate": "Bearer"})
    return LoginResponse(message="เข้าสู่ระบบสำเร็จ", access_token=create_session(user), user=to_user_dto(user))


@router.get("/status", response_model=LoginStatusResponse)
def login_status(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> LoginStatusResponse:
    if credentials is None or credentials.scheme.lower() != "bearer":
        return LoginStatusResponse(logged_in=False)
    user = get_user_by_token(credentials.credentials)
    return LoginStatusResponse(logged_in=user is not None, user=to_user_dto(user) if user else None)


@router.get("/me", response_model=UserDTO)
def me(user: User = Depends(require_login)) -> UserDTO:
    return to_user_dto(user)


@router.post("/logout", response_model=MessageResponse)
def logout(credentials=Depends(bearer_scheme), user: User = Depends(require_login)) -> MessageResponse:
    delete_session(credentials.credentials)
    return MessageResponse(message="ออกจากระบบสำเร็จ")
