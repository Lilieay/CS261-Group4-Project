# Task5: U1 — กำหนด Login API และวิธีเก็บสถานะผู้ใช้

## ขอบเขต

เอกสารนี้อธิบาย Login API ที่ใช้งานแล้ว ได้แก่ เข้าสู่ระบบ ตรวจสถานะ อ่านบัญชีปัจจุบัน และออกจากระบบ การยืนยันบัญชีใช้ TU adapter ส่วน User อยู่ใน SQL Server และ Session อยู่ใน memory ของ backend

## หลักการยืนยันตัวตนและสถานะผู้ใช้

1. ผู้ใช้ส่ง `username` และ `password` ไปที่ `POST /api/auth/login`
2. Service เรียก `verify_tu_account()` เพื่อตรวจบัญชีกับ TU API หรือโหมด mock ตามการตั้งค่าใน `.env`
3. AuthService รับเฉพาะ TUAccount ที่เป็น student และ active สำหรับ real mode adapter กำหนด active ภายในหลังยอมรับ status/type/name ไม่ใช่การตรวจสถานะลงทะเบียนเรียนแยกอีกครั้ง
4. AuthService บันทึก User และ commit ก่อนสร้าง token แบบสุ่ม เก็บ `token -> LoginSession` ใน `_sessions` โดย LoginSession มี AuthenticatedUser และ expires_at
5. การเรียก API ที่ต้อง Login ต้องส่ง `Authorization: Bearer <access_token>`
6. ระบบไม่เก็บ password ไว้ใน `User` หรือใน session และไม่ส่ง password กลับใน Response

Session มีอายุเริ่มต้น 8 ชั่วโมง ปรับด้วย AUTH_SESSION_TTL_SECONDS ซึ่งเป็นวินาทีที่มากกว่า 0 get_user ตรวจ deadline ทุกครั้งที่ใช้ token และลบ Session ที่หมดอายุ การ restart backend ทำให้ Session หายและต้อง Login ใหม่ ไม่มีตาราง Token หรือ Session ในฐานข้อมูล

## บัญชี mock และกติกาของหน้าเว็บ

บัญชีเริ่มต้นในโหมด mock คือ `6800000000 / 0000000000000` เป็นข้อมูลสมมติ ไม่ใช่บัญชีหรือเลขบัตรประชาชนจริง รหัสผ่าน 13 หลักนี้ใช้สำหรับ mock เท่านั้น ไม่ใช่ข้อบังคับรหัสผ่านจริง หากกำหนด `TU_MOCK_USERNAME` หรือ `TU_MOCK_PASSWORD` ใน environment ของ Backend ค่านั้นจะทับค่าเริ่มต้น

หน้า Login รับ username เฉพาะตัวเลข ความยาวไม่เกิน 50 หลัก ส่วน API ตรวจ username เป็น string ความยาว 1–50 ตัวอักษรและตัดช่องว่างหัวท้ายก่อนยืนยันบัญชี จึงต้องแยกกติกาของฟอร์มออกจากกติกา API

Frontend เก็บเฉพาะ token ใน `sessionStorage` key `access_token` เพื่อส่ง Bearer token ส่วน session ที่จับคู่ token กับผู้ใช้อยู่ในหน่วยความจำของ Backend ไม่เก็บรหัสผ่านใน browser storage

## API Contract

### `POST /api/auth/login`

ใช้ตรวจสอบข้อมูลบัญชีและสร้าง Login session ไม่ต้องใช้ Bearer token

#### Request

```http
POST /api/auth/login
Content-Type: application/json
```

```json
{
  "username": "6800000000",
  "password": "0000000000000"
}
```

| ฟิลด์ | ชนิด | กติกา |
|---|---|---|
| `username` | string | บังคับ ความยาว 1–50 ตัวอักษร ระบบจะตัดช่องว่างหัวท้ายก่อนตรวจสอบ |
| `password` | string | บังคับ ความยาว 1–100 ตัวอักษร ไม่เก็บค่าลง User หรือ session |

#### สำเร็จ — `200 OK`

```json
{
  "message": "เข้าสู่ระบบสำเร็จ",
  "access_token": "<random-session-token>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "6800000000",
    "display_name": "Student User",
    "role": "student"
  }
}
```

### `GET /api/auth/status`

ตรวจสถานะ Login โดยไม่บังคับให้มี token

#### Request

```http
GET /api/auth/status
Authorization: Bearer <access_token>
```

#### มี session — `200 OK`

```json
{
  "logged_in": true,
  "user": {
    "id": 1,
    "username": "6800000000",
    "display_name": "Student User",
    "role": "student"
  }
}
```

#### ไม่มี token หรือ token ไม่ถูกต้อง — `200 OK`

```json
{
  "logged_in": false,
  "user": null
}
```

### `GET /api/auth/me`

อ่านข้อมูลผู้ใช้จาก session ปัจจุบัน ต้องส่ง Bearer token

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### สำเร็จ — `200 OK`

```json
{
  "id": 1,
  "username": "6800000000",
  "display_name": "Student User",
  "role": "student"
}
```

### `POST /api/auth/logout`

ยกเลิก session ปัจจุบันและทำให้ token เดิมใช้เรียก `/api/auth/me` ไม่ได้

Backend ต้องตรวจ token ก่อน Logout หาก token หมดอายุแล้วจะตอบ 401 ส่วน frontend ปัจจุบันยอมรับ 401 ของ Logout เพื่อล้าง token ใน browser และกลับหน้า Login

```http
POST /api/auth/logout
Authorization: Bearer <access_token>
```

#### สำเร็จ — `200 OK`

```json
{
  "message": "ออกจากระบบสำเร็จ"
}
```

## ข้อผิดพลาด

| HTTP | เงื่อนไข | รูปแบบ Response ที่ใช้อยู่ |
|---|---|---|
| `401` | username/password ไม่ถูกต้อง บัญชีไม่ active หรือ TU API ยืนยันไม่ได้ | `{"detail": "เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง"}` |
| `401` | เรียก `/me` หรือ `/logout` โดยไม่มี Bearer token | `{"detail": "กรุณาส่ง Bearer token เพื่อยืนยันตัวตน"}` |
| `401` | token ไม่ถูกต้องหรือหมดอายุ | `{"detail": "Token ไม่ถูกต้องหรือหมดอายุ"}` |
| `422` | Request ไม่ตรงชนิดข้อมูลหรือไม่ผ่านข้อกำหนดของ Pydantic | FastAPI validation response พร้อมรายละเอียด `detail` |
| `503` | SQLAlchemyError ระหว่างสร้าง/อัปเดต User หรือ commit | `{"detail":"ไม่สามารถเข้าสู่ระบบได้ในขณะนี้"}` และไม่ออก token |

โค้ดปัจจุบันใช้ข้อความ Login failure เดียวกันสำหรับข้อมูลผิด บัญชีที่ไม่ผ่านเงื่อนไข และ TUVerificationError จึงยังไม่แยกข้อความ outage ตาม DoD เดิม ตารางนี้อธิบาย backend; Node auth proxy และหน้า Login อาจแทนข้อความผิดพลาดด้วยข้อความกลาง และ proxy ตอบ 502 เมื่อ upstream ใช้ไม่ได้

## DTO Schema ตาม Pydantic

| DTO | ใช้กับ | ฟิลด์ |
|---|---|---|
| `LoginRequest` | Request ของ `POST /api/auth/login` | `username: str`, `password: str` |
| `UserDTO` | ข้อมูลผู้ใช้ที่เปิดเผยได้ | `id: int`, `username: str`, `display_name: str`, `role: str` |
| `LoginResponse` | Response เมื่อ Login สำเร็จ | `message: str`, `access_token: str`, `token_type: str`, `user: UserDTO` |
| `LoginStatusResponse` | Response ของ `/status` | `logged_in: bool`, `user: UserDTO | null` |
| `MessageResponse` | Response ของ `/logout` | `message: str` |

ไม่รวม password ใน `UserDTO`, `LoginResponse` หรือ session data

## การแบ่งหน้าที่ของโค้ด

| ส่วน | หน้าที่ |
|---|---|
| `backend/app/routers/auth.py` | ประกาศ endpoint, แปลง AuthenticatedUser เป็น UserDTO และกำหนด HTTP status |
| `backend/app/dependencies.py` | current_user ตรวจ Bearer token ผ่าน AuthService และ get_auth_service อ่าน instance จาก app.state |
| `backend/app/schemas/auth.py` | ประกาศ Request/Response DTO และ validation ด้วย Pydantic |
| `backend/app/services/auth.py` | login/get_user/logout ควบคุม User transaction และ Session ที่มีวันหมดอายุ |
| `backend/app/services/tu_api.py` | ตรวจบัญชี TU API จริงหรือ mock ตาม configuration |
| `backend/app/main.py` | รวม `auth_router` เข้ากับ FastAPI application |

## แผนภาพ Router/API กับ DTO

```mermaid
flowchart LR
    Client[หน้าเว็บหรือ API Client] --> Login[POST /api/auth/login]
    Login --> LoginRequest[LoginRequest]
    Login --> AuthService[AuthService.login]
    AuthService --> TU[tu_api.verify_tu_account]
    AuthService --> UserDAO[UserDAO และ SQL Server]
    AuthService --> Session[AuthService._sessions]
    Session --> LoginResponse[LoginResponse + UserDTO]

    Client --> Status[GET /api/auth/status]
    Client --> Me[GET /api/auth/me]
    Client --> Logout[POST /api/auth/logout]
    Me --> Bearer[current_user / Bearer token]
    Logout --> Bearer
    Bearer --> Session
    Status --> LoginStatus[LoginStatusResponse]
    Me --> User[UserDTO]
    Logout --> Message[MessageResponse]
```

แผนภาพนี้แสดงความสัมพันธ์ระหว่าง Client, Router, DTO, Service และ session store ตามโค้ดจริง ไม่ได้กำหนดการเก็บ session ถาวรในฐานข้อมูล

## เกณฑ์ตรวจรับ

- มีวิธีเรียก API ครบทั้ง Login, ตรวจสถานะ, อ่านผู้ใช้ปัจจุบัน และ Logout
- มี Request/Response ตัวอย่างและกติกาฟิลด์ตาม Pydantic Schema
- ระบุกรณี `401` และ `422` ตามพฤติกรรมของ API จริง
- ระบุชัดว่า session เก็บแบบ in-memory และใช้ Bearer token
- ไม่ส่งหรือเก็บ password ใน User DTO หรือ session
- แผนภาพแสดง Router/API, DTO, Service, TU API และ session store

ดู [AuthService](../../../backend/app/services/auth.py), [Auth Router](../../../backend/app/routers/auth.py), [Auth DTO](../../../backend/app/schemas/auth.py), [TU adapter](task11-tu-api-verification.md) และ [Sequence Login](task7-login-sequence-diagram.md)
