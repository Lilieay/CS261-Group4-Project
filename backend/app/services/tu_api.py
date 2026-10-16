import os
import secrets

import httpx

from app.schemas.tu_auth import TUVerifyResponse


def _mock_verify(username: str, password: str) -> TUVerifyResponse:
    """ผลจำลองสำหรับทดสอบโดยไม่ใช้บัญชี TU จริง"""
    mock_username = os.getenv("TU_MOCK_USERNAME", "mock_student")
    mock_password = os.getenv("TU_MOCK_PASSWORD", "mock_password")
    verified = secrets.compare_digest(username, mock_username) and secrets.compare_digest(password, mock_password)
    return TUVerifyResponse(
        verified=verified,
        message="ยืนยันบัญชีจำลองสำเร็จ" if verified else "ชื่อผู้ใช้หรือรหัสผ่านจำลองไม่ถูกต้อง",
        source="mock",
    )


def verify_with_tu_api(username: str, password: str) -> TUVerifyResponse:
    """เรียก TU API จริงเมื่อกำหนด TU_API_MODE=real มิฉะนั้นใช้ mock"""
    mode = os.getenv("TU_API_MODE", "mock").lower()
    if mode != "real":
        return _mock_verify(username, password)

    url = os.getenv("TU_API_URL")
    api_key = os.getenv("TU_API_KEY")
    if not url:
        return TUVerifyResponse(verified=False, message="ยังไม่ได้ตั้งค่า TU_API_URL", source="tu_api")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        response = httpx.post(
            url,
            json={"username": username, "password": password},
            headers=headers,
            timeout=10.0,
        )
        if response.status_code in (401, 403):
            return TUVerifyResponse(verified=False, message="TU API ปฏิเสธการยืนยันบัญชี", source="tu_api")
        response.raise_for_status()
        data = response.json()
        verified = bool(data.get("verified", data.get("success", False)))
        return TUVerifyResponse(
            verified=verified,
            message="ยืนยันบัญชีกับ TU API สำเร็จ" if verified else "TU API ยืนยันบัญชีไม่ผ่าน",
            source="tu_api",
        )
    except (httpx.HTTPError, ValueError):
        return TUVerifyResponse(verified=False, message="ไม่สามารถเชื่อมต่อ TU API ได้", source="tu_api")
