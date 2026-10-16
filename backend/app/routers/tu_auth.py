from fastapi import APIRouter

from app.schemas.tu_auth import TUVerifyRequest, TUVerifyResponse
from app.services.tu_api import verify_with_tu_api

router = APIRouter(prefix="/api/auth", tags=["TU Authentication"])


@router.post("/verify-tu", response_model=TUVerifyResponse)
def verify_tu_account(payload: TUVerifyRequest) -> TUVerifyResponse:
    """ยืนยันบัญชีผ่าน TU API หรือ mock ตามค่า TU_API_MODE"""
    return verify_with_tu_api(payload.username, payload.password)
