# CS261 Group 4 — Task12: Login API และสถานะ Login

โปรเจกต์นี้เพิ่มระบบ Login API ด้วย FastAPI โดยมี DTO สำหรับรับข้อมูลและส่งข้อมูลกลับอย่างชัดเจน พร้อมสร้างสถานะการเข้าสู่ระบบจาก Bearer token

## วิธีเปิด Backend

เปิด PowerShell ที่โฟลเดอร์ `backend` แล้วรันคำสั่ง:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

เปิดเอกสาร API ได้ที่ http://127.0.0.1:8000/docs

## DTO ที่ใช้

- `LoginRequest`: รับ `username` และ `password` โดยห้ามเป็นค่าว่าง
- `UserDTO`: ข้อมูลผู้ใช้ที่เปิดเผยได้ ได้แก่ `id`, `username`, `display_name` และ `role` โดยไม่ส่ง password กลับไป
- `LoginResponse`: ข้อความผลลัพธ์, `access_token`, ประเภท token และ `UserDTO`
- `LoginStatusResponse`: `logged_in` และข้อมูลผู้ใช้เมื่อมี session ที่ถูกต้อง

## API ที่สร้าง

| Method | Path | หน้าที่ | ต้องใช้ token |
|---|---|---|---|
| POST | `/api/auth/login` | ตรวจสอบชื่อผู้ใช้/รหัสผ่านและสร้าง session | ไม่ต้องใช้ |
| GET | `/api/auth/status` | ตรวจสถานะ Login ปัจจุบัน | ไม่บังคับ |
| GET | `/api/auth/me` | อ่านข้อมูลผู้ใช้ของ token ปัจจุบัน | ต้องใช้ |
| POST | `/api/auth/logout` | ลบ session และทำให้ token ใช้งานไม่ได้ | ต้องใช้ |

เมื่อ Login สำเร็จ ให้นำค่า `access_token` ไปส่งใน Header ดังนี้:

```text
Authorization: Bearer <access_token>
```

## บัญชีสำหรับทดสอบ

| username | password | role |
|---|---|---|
| `student` | `password123` | student |
| `admin` | `admin123` | admin |

## ตัวอย่างเรียก API

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"password123"}'
```

ตรวจสถานะ Login:

```bash
curl http://127.0.0.1:8000/api/auth/status \
  -H "Authorization: Bearer <access_token>"
```

## ผลการทดสอบ API

รันการทดสอบด้วยคำสั่ง `pytest` จากโฟลเดอร์ `backend` ผลที่คาดหวังคือทุกกรณีผ่าน:

| กรณีทดสอบ | ข้อมูลทดสอบ | ผลที่คาดหวัง |
|---|---|---|
| Login สำเร็จ | `student / password123` | HTTP 200, ได้ token และ `logged_in=true` |
| รหัสผ่านผิด | `student / wrong` | HTTP 401 และไม่สร้าง session |
| Logout | token ที่ได้จาก Login | HTTP 200 และ token เดิมใช้ดู `/me` ไม่ได้ (HTTP 401) |

## หมายเหตุด้านการเก็บข้อมูล

โค้ดชุดนี้เก็บผู้ใช้และ session ไว้ในหน่วยความจำเพื่อให้เหมาะกับการสาธิตและการทดสอบ Task เมื่อหยุดหรือ restart server session จะหายทั้งหมด สำหรับระบบจริงควรเปลี่ยนเป็นฐานข้อมูล, เก็บ password เป็น hash และใช้ token/session store ที่มีอายุหมดอายุและรองรับหลาย instance

## Task11: ยืนยันบัญชีกับ TU API

การ Login เรียก service ยืนยันบัญชีกับ TU API ก่อนสร้าง session โดยค่าเริ่มต้นใช้ Mock สำหรับทดสอบในเครื่อง และเปลี่ยนเป็น TU API จริงได้ด้วย `TU_API_MODE=real`, `TU_API_URL` และ `TU_API_TIMEOUT` ในไฟล์ `.env` ห้าม commit ข้อมูลลับจริง

ระบบอนุญาตเฉพาะบัญชีนักศึกษาที่มีสถานะ active และ fail-closed เมื่อ TU API ใช้งานไม่ได้หรือข้อมูลยืนยันไม่ครบ รายงาน Task11 อยู่ที่ `docs/U1/Task11-tu-api-verification.md`

