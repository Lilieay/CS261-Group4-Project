# Task16: สรุปผลตรวจสอบ Backend และ Docker

## รุ่นและสภาพแวดล้อม

- Branch: `feat/task16-backend-docker`
- Source revision: `4e1bd37d1c9ee262f73aa54471d5e2c7a43fec37`
- สภาพแวดล้อมทดสอบอัตโนมัติ: Windows, Python 3.14.6, SQLite สำหรับ test
- Backend image: Python 3.14.8, image SHA `sha256:8ce7b519376d05894f37f192df7c9a157742a85376df16cc4ea5819749f7f544`
- Frontend: Node.js 24.22.0
- Docker Compose: 5.5.1; SQL Server: 2022

## ผลทดสอบอัตโนมัติ

| รายการ | คำสั่งหรือหลักฐาน | ผล |
|---|---|---|
| Backend test suite | จากโฟลเดอร์ `backend`: `.venv\Scripts\python.exe -m pytest -p no:cacheprovider test -q` | ผ่าน 106 tests และ 46 subtests |
| Login, status, logout, login ซ้ำ และ database error | `backend/test/test_auth.py` | ผ่าน รวมกรณี 401 และ 503 |
| TU adapter แบบ real โดยแทน HTTP transport ใน test | `backend/test/test_auth.py`, `backend/test/test_tu_api_real.py` | ผ่าน ไม่มีการเรียก TU จริง |
| Read, publish, update และ delete guide APIs | `backend/test/test_read_guide_api.py`, `backend/test/test_publish_guide_api.py`, `backend/test/test_my_guides_api.py`, `backend/test/test_my_guide_updates_api.py`, `backend/test/test_my_guide_deletions_api.py` | ผ่านบน SQLite และ AuthService ที่แยกสำหรับ test |

รัน suite ซ้ำใน backend container ด้วย test directory แบบ read-only ผลคือ 106 tests ผ่าน และ 46 subtests ผ่าน มี deprecation warning เดิมจาก Starlette/httpx หนึ่งรายการ ซึ่งไม่ทำให้ test ล้มเหลว

## ผลตรวจ runtime ที่ได้แล้ว

### ตรวจซ้ำหลังรวม Course API จาก PR #80 (2026-10-19)

- Source revision ก่อนแก้ fixture: `b173855` พร้อมการเปลี่ยนแปลง fixture ใน commit ที่เพิ่มบันทึกนี้
- `backend/test/test_course_api.py` ใช้ `AuthService` กับ SQLite ของชุดทดสอบผ่าน dependency `get_auth_service` แทนการ patch ตัวแปร `USERS`/`ACTIVE_SESSIONS` ที่เลิกใช้แล้ว โดยยังเรียก Login และตรวจ Bearer token จริง
- จากโฟลเดอร์ `backend`, กำหนด `DB_CONNECTION_STRING` จำลองสำหรับ import แอป แล้วรัน `.venv\Scripts\python.exe -m pytest -p no:cacheprovider test -q` ด้วย `TU_API_MODE=mock`: **112 tests และ 54 subtests ผ่าน** บน Windows/Python 3.14.6
- รันเฉพาะ `test/test_course_api.py` ด้วย `TU_API_MODE=invalid-test-mode`: **6 tests และ 8 subtests ผ่าน** ยืนยันว่า verifier จำลองไม่ขึ้นกับ TU environment
- ผลรอบนี้เป็น SQLite/TestClient ไม่ได้รัน Docker, SQL Server, browser หรือ TU จริงซ้ำ ผล runtime ด้านล่างยังเป็นผลของรุ่นที่ระบุเดิม

- `scripts/start-backend.ps1` เริ่ม SQL Server และ backend ได้ Backend root ตอบ 200
- รัน `scripts/start-backend.ps1` รอบที่สองผ่าน ฐานข้อมูล ตาราง และ user mock เดิมยังอยู่; username mock มีหนึ่งแถวและ ID `1002` คงเดิม
- `docker compose up -d --build frontend` เริ่ม frontend ได้
- HTTP ผ่าน proxy ที่พอร์ต 5000 ผ่าน login, status, me, login ซ้ำ และ logout การ login ซ้ำคืน database user ID `1002`; หลัง logout คำขอ me เดิมตอบ 401
- หลัง restart backend process, token เดิมตอบ 401 ที่ me และ status แสดง `logged_in=false`; login ใหม่คืน database user ID `1002`
- SQL Server smoke test ผ่านการ login ซ้ำด้วย AuthService และ UserDAO จริง ได้ user row เดียวและ database ID เดิม Logout ผ่าน และ service instance ใหม่ปฏิเสธ token เก่า
- Isolated storage-failure probe ใน backend container ตอบ 503 โดยไม่ออก token เมื่อ ODBC เชื่อมต่อไป `127.0.0.1:1` ล้มเหลว Production SQL Server ยังทำงานตามปกติ
- ลบ temporary user ที่สร้างเพื่อทดสอบแล้ว จำนวนแถวก่อนเริ่มและหลังจบการตรวจคือ users 2, courses 24, guides 0 และไม่เหลือผู้ใช้ชั่วคราว ข้อมูล user, course และ guide เดิมยังอยู่
- Chrome แสดงข้อความ required สำหรับช่องว่างทั้งสองช่อง, numeric validation สำหรับ username ที่มีตัวอักษร, ข้อความทั่วไปเมื่อรหัสผ่านผิด และเปิด `courses.html` เมื่อ login mock สำเร็จ
- เมื่อหยุด backend แล้วส่ง login ที่ถูกต้อง หน้าเว็บแสดงข้อความทั่วไปและเปิดใช้งานช่องกรอกกับปุ่มอีกครั้ง หลังเริ่ม backend ใหม่และรอ root readiness การ retry เปิด `courses.html` สำเร็จ
- OpenAPI มี 11 paths ก่อนและหลัง runtime checks โดยรายการ guide methods ยังคงอยู่ครบ

การตรวจ runtime ตามแผนเสร็จแล้ว ไม่มีการเรียก TU จริง

## รายงานตรวจระบบ

ผล runtime แยกตามรายงานย่อยด้านล่าง

- [UI กับ API](U1_Task16_UI_API_Test_Report.md)
- [API กับฐานข้อมูล](U1_Task16_API_DAO_Test_Report.md)
- [ระบบ Docker และ end-to-end](U1_Task16_System_Test_Report.md)
- [คู่มือเริ่ม Backend และ Docker](U1_Task16_Backend_Docker_Runbook.md)

## ขอบเขต

ชุดทดสอบใช้ SQLite และ mock TU adapter หรือแทน HTTP transport จึงไม่พิสูจน์การเชื่อมต่อ TU จริง การตรวจ runtime ใช้ TU mock ไม่มีการเรียก endpoint จริงหรือบันทึก credential
