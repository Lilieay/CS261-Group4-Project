from fastapi import APIRouter, Depends

from app.dependencies.auth import require_login
from app.routers.auth import to_user_dto
from app.schemas.auth import UserDTO
from app.services.auth import User

router = APIRouter(prefix="/api/protected", tags=["Protected API"])


@router.get("/check", response_model=UserDTO)
def protected_check(user: User = Depends(require_login)) -> UserDTO:
    """ตัวอย่าง API อื่นที่เรียกใช้ตัวตรวจสถานะ Login กลาง"""
    return to_user_dto(user)
