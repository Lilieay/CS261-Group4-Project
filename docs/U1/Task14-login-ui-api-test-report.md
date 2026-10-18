# Task14: เชื่อมหน้า Login กับ API

## ผลงานที่ส่งมอบ

- `frontend/public/js/login.js` เรียก `POST /api/auth/login` ด้วยข้อมูล JSON จากฟอร์มจริง
- เมื่อสำเร็จ เก็บ `access_token` ใน `localStorage` ที่ key `cs261_access_token` และแสดงชื่อผู้ใช้จากผล API
- เมื่อผิดพลาด แสดงข้อความจาก API หรือข้อความกรณี Backend ไม่พร้อมใช้งาน
- `backend/app/main.py` อนุญาต CORS จาก Frontend ที่ `127.0.0.1:5000` และ `localhost:5000`
- ปุ่ม University Account แสดงว่ายังไม่เปิดใช้งานจริง ไม่ได้จำลองว่า Login สำเร็จ

## Test report

| กรณี | Request / ข้อมูลทดสอบ | ผลที่คาดหวัง | ผลจริง | สถานะ |
|---|---|---|---|---|
| UI-API Login สำเร็จ | `POST /api/auth/login`, `student / password123` | HTTP 200, ได้ token และชื่อผู้ใช้ | โค้ด UI ส่ง request จริงและเก็บ token ตาม response | IMPLEMENTED |
| UI-API รหัสผ่านผิด | `POST /api/auth/login`, `student / wrong` | HTTP 401, ไม่เก็บ token ใหม่ | โค้ด UI แสดง `detail` จาก API | IMPLEMENTED |
| API ตรวจสถานะ | `GET /api/auth/status` พร้อม Bearer token | `logged_in: true` | มี automated test รองรับใน `backend/test/test_auth.py` แต่ยังรันไม่ได้เพราะเครื่องนี้ไม่มี pytest/FastAPI | NOT RUN |
| API Logout | `POST /api/auth/logout` พร้อม token | HTTP 200 และ token เดิมใช้ `/me` ไม่ได้ | มี automated test รองรับใน `backend/test/test_auth.py` แต่ยังรันไม่ได้เพราะเครื่องนี้ไม่มี pytest/FastAPI | NOT RUN |
| UI Backend ไม่พร้อม | ปิด Backend แล้ว Submit | แจ้งข้อผิดพลาดการเชื่อมต่อ | โค้ด UI ดัก `fetch` error และแสดงข้อความ | IMPLEMENTED |

## ขอบเขตหลักฐาน

บัญชี `student / password123` และ session เป็นข้อมูลสาธิตในหน่วยความจำตาม Backend ปัจจุบัน ไม่ใช่ TU/University SSO จริง การเชื่อมต่อ UI กับ `/api/auth/login` เป็นการเรียก API จริง ส่วนปุ่ม University Account ยังไม่ทำการเชื่อมต่อภายนอกและจะแจ้งสถานะตามจริง

## การตรวจสอบที่รันได้ในสภาพแวดล้อมนี้

- `node --check frontend/public/js/login.js` ผ่าน
- `git diff --check` ผ่าน
- ไม่สามารถรัน `pytest` ได้ เนื่องจาก runtime ของเครื่องไม่มีแพ็กเกจ `pytest` และ `fastapi`; ไม่ได้ติดตั้ง dependency เพิ่ม
