# Task28: U2 — Course API และ DTO

## ขอบเขต

เพิ่ม Course API สำหรับผู้ใช้ที่ผ่าน Login เดิมแล้ว เพื่อดึงรายวิชารหัส `CS` ค้นหาด้วยรหัสหรือชื่อ และเปิดดูรายละเอียดรายวิชา โดย Response ใช้ `CourseDTO` ที่ตรงกับข้อมูล `Course` ในระบบ

## API และ DTO ที่ส่งมอบ

| API | Method | หน้าที่ | DTO |
|---|---|---|---|
| `/courses` | `GET` | ดึงรายวิชา CS ทั้งหมด | `list[CourseDTO]` |
| `/courses?search=CS261` | `GET` | ค้นหาจากรหัสขึ้นต้นหรือชื่อที่มีคำค้น | `list[CourseDTO]` |
| `/courses/{course_id}` | `GET` | เปิดรายละเอียดรายวิชา CS หนึ่งรายการ | `CourseDTO` |

ทุก endpoint ใช้ Bearer token จาก Login API เดิม หากไม่มีหรือ token ไม่ถูกต้องจะตอบ `401 AUTH_REQUIRED`

`CourseDTO` ประกอบด้วย `id`, `course_code`, `course_name`, `instructor_name` และ `description` โดยไม่ส่ง password หรือ token ในข้อมูลรายวิชา

## ตารางผล API Test

| รหัสกรณี | ข้อมูลทดสอบ | ผลที่คาดหวัง | ผลจริง | สถานะ | หลักฐาน |
|---|---|---|---|---|---|
| COURSE-API-01 | Login ด้วยบัญชีทดสอบที่ verifier ถูกแทนที่ แล้ว `GET /courses` | HTTP 200 และทุกรายการเป็นรหัส `CS` | HTTP 200; รายการเป็น `CS102`, `CS261` | ผ่าน | `backend/test/test_course_api.py` |
| COURSE-API-02 | `GET /courses?search=CS261` | HTTP 200 และคืนรายการที่รหัสตรงคำค้น | HTTP 200; คืน `CS261` | ผ่าน | `backend/test/test_course_api.py` |
| COURSE-API-03 | `GET /courses?search=software` | HTTP 200 และค้นจากชื่อรายวิชาได้ | HTTP 200; คืน `CS261` | ผ่าน | `backend/test/test_course_api.py` |
| COURSE-API-04 | `GET /courses/{course_id}` ของรายวิชาที่มีอยู่ | HTTP 200 และฟิลด์ DTO ครบ | HTTP 200; DTO ตรงค่าที่กำหนดใน fixture | ผ่าน | `backend/test/test_course_api.py` |
| COURSE-API-05 | `GET /courses/999` | HTTP 404 พร้อม `COURSE_NOT_FOUND` | HTTP 404; `COURSE_NOT_FOUND` | ผ่าน | `backend/test/test_course_api.py` |
| COURSE-API-06 | เรียก `/courses` โดยไม่ส่ง Authorization | HTTP 401 พร้อม `AUTH_REQUIRED` | HTTP 401; `AUTH_REQUIRED` | ผ่าน | `backend/test/test_course_api.py` |

## ผลตรวจใน worktree

- Source revision ก่อนแก้ไข: `b6a06648d054a9801c22a63bf57b1117c901a8b8`; ผลด้านล่างมาจาก revision นี้พร้อมการเปลี่ยนแปลงใน worktree PR80 ปัจจุบัน ไม่ใช่ผลจาก commit ใหม่
- วันที่ตรวจ: 2026-10-19; Python 3.14.6
- `python -m unittest discover -s test -p test_course_api.py -v`: ผ่าน 6 tests ด้วย SQLite in-memory และ TU environment ที่ตั้งเป็นค่าผิดโดยเจตนา; การทดสอบ patch verifier ใน `app.services.auth` จึงยังใช้ login/token/Bearer route จริงโดยไม่เรียก TU
- `python -m pytest -p no:cacheprovider test -q`: ผ่าน 102 tests และ 54 subtests; ใช้ `DB_CONNECTION_STRING` แบบจำลองและ `TU_API_MODE=mock` เพื่อ import/configure แอป โดยไม่มีการเชื่อมต่อ SQL Server
- การค้นหา `%`, `_`, `folder/%_` คืนรายการตรงตัวอักษรและไม่คืนข้อมูล non-CS ที่มีอักขระเดียวกัน
- ไม่ได้ทดสอบกับ SQL Server, Postman/browser หรือ TU จริง

## Postman และข้อมูลที่ใช้

ใช้ `Task28-course-api.postman_collection.json` โดยต้องกรอก password ใน Environment ของผู้ทดสอบเองก่อนรัน Login Collection ไม่เก็บ password จริงหรือ token จริงไว้ในไฟล์ Collection

ค่าตัวอย่างที่ใช้ทดสอบ:

- `base_url`: `http://127.0.0.1:8000`
- `username`: `6800000000` (ค่า mock เริ่มต้น; รหัสผ่าน mock คือ `0000000000000` เมื่อรันแอปในโหมด mock)
- `search`: `CS261`
- `course_id`: `1` หรือ ID ของรายวิชาที่มีอยู่ในฐานข้อมูลจริง

## โครงสร้างโค้ด

- `CourseApiRoute` แปลงข้อผิดพลาดเป็น Error DTO รูปแบบเดียวกับ API อ่านข้อมูลเดิม
- `CourseService` แปลง Entity เป็น `CourseDTO` และตรวจกรณีไม่พบรายวิชา
- `CourseDAO` ค้นหาเฉพาะรหัส `CS` และรองรับค้นหาด้วยรหัสขึ้นต้นหรือชื่อรายวิชา
- Router ใช้ `current_user` ตัวเดียวกับ Login API เดิม

## ข้อจำกัดและการตรวจรับ

- การค้นหาจำกัดความยาวคำค้นไม่เกิน 255 ตัวอักษรตาม API contract
- รายวิชาที่ไม่ใช่รหัส `CS` จะไม่ถูกส่งออกจาก Course API
- ผลในตารางมาจาก API integration tests บน SQLite และ verifier จำลอง ไม่ใช่การยืนยันบัญชี TU จริง
- ก่อนทดสอบ Postman ต้องกำหนด `DB_CONNECTION_STRING`, seed ฐานข้อมูล และเปิดใช้ TU mock; ผล SQL Server และ Postman/browser ยังไม่ได้ตรวจในงานนี้
