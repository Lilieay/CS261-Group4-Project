# Task14: เชื่อมหน้า Login กับ API

## ผลงานที่ส่งมอบ

- `frontend/public/js/login.js` ส่ง JSON ไป `POST /api/auth/login` ผ่าน proxy ใน `frontend/src/server.js` ซึ่งส่งต่อไป Backend ตาม `BACKEND_URL`
- เมื่อสำเร็จ เก็บเฉพาะ token ใน `sessionStorage` ที่ key `access_token` แล้วนำไป `courses.html` ไม่เก็บรหัสผ่าน
- หน้า Login รับรหัสนักศึกษาเป็นตัวเลข และใช้ข้อมูล mock เริ่มต้น `6800000000 / 0000000000000` ซึ่งเป็นข้อมูลสมมติ ไม่ใช่บัญชีหรือเลขบัตรประชาชนจริง
- รหัสผ่าน 13 หลักเป็นเพียงข้อมูล mock ไม่ใช่กฎบังคับรหัสผ่านจริง
- เมื่อ Login ถูกปฏิเสธ, response ไม่ถูกต้อง หรือเชื่อมต่อ Backend ไม่ได้ จะแสดงข้อความกลาง: “เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง” ไม่แสดง `detail` จาก API
- หน้า Login ปัจจุบันไม่มีปุ่ม University Account
- `backend/app/main.py` อนุญาต CORS จาก `http://127.0.0.1:5000` และ `http://localhost:5000` สำหรับ GET, POST และ OPTIONS ทั้งนี้ proxy ปัจจุบันใช้ origin เดียวกับหน้าเว็บ จึงไม่ต้องพึ่ง CORS สำหรับเส้นทางนี้

## การตั้งค่า mock

ใช้ `TU_API_MODE=mock` (ค่าเริ่มต้น) บัญชีเริ่มต้นคือ `6800000000 / 0000000000000` หาก environment ของ Backend กำหนด `TU_MOCK_USERNAME` หรือ `TU_MOCK_PASSWORD` อยู่แล้ว ค่านั้นจะทับค่าเริ่มต้น ต้องใช้ข้อมูลให้ตรงกับ environment และ username ต้องเป็นตัวเลขเพื่อผ่านฟอร์ม

## การตั้งค่า TU API จริง

โหมดจริงใช้ `TU_API_MODE=real` และอ่านค่าลับจาก environment เท่านั้น ห้ามใส่ Token Key หรือรหัสผ่านจริงลงใน source code, Postman Collection หรือ Git:

```text
TU_API_MODE=real
TU_API_URL=<TU Authentication API endpoint>
TU_API_KEY=<Application-Key จาก TU API Developer>
TU_API_TIMEOUT=5
```

Backend จะส่ง `UserName` และ `PassWord` ใน JSON พร้อม Header `Application-Key` และรับ Response ที่มี `status=true`, `type=student` และ `displayname_th` หรือ `displayname_en` ตาม Contract ของ TU Authentication API หากไม่ผ่านเงื่อนไขจะปฏิเสธ Login แบบเดียวกับบัญชีไม่ถูกต้อง

## สถานะ UI–API จากการตรวจโค้ด

ตารางนี้เป็นการตรวจเส้นทางโค้ด ไม่ใช่ผลทดสอบผ่าน browser จริง การทดสอบ Docker และ System Test อยู่ใน Task16

| กรณี | ข้อมูล / ขั้นตอน | พฤติกรรมตามโค้ด | สถานะ |
|---|---|---|---|
| Login สำเร็จ | `6800000000 / 0000000000000` | ส่ง request ผ่าน proxy เก็บ token ใน sessionStorage และไป courses.html | รอทดสอบผ่าน browser |
| รหัสผ่านผิด | `6800000000 / wrong` | Backend ปฏิเสธ หน้าเว็บแสดงข้อความกลางและไม่เก็บ token ใหม่ | รอทดสอบผ่าน browser |
| รูปแบบ username ผิด | `student` | ฟอร์มแจ้งว่าต้องเป็นตัวเลขและไม่ส่ง request | รอทดสอบผ่าน browser |
| Backend ไม่พร้อม | หยุด Backend แล้ว submit ข้อมูลที่ผ่าน validation | proxy ตอบข้อผิดพลาด หน้าเว็บแสดงข้อความกลาง | รอทดสอบผ่าน browser |

## ขอบเขตหลักฐาน

mock เป็นการจำลอง TU verification สำหรับพัฒนา ไม่ใช่ TU/University SSO จริง Backend ใน PR นี้เก็บ user และ session ในหน่วยความจำ ส่วน browser เก็บเฉพาะ token ใน sessionStorage การบันทึกผู้ใช้ผ่าน DAO และ SQL Server จะรวมและทดสอบใน Task16

## การตรวจสอบ

- ผลการตรวจโค้ด UI และ proxy: ตามตารางด้านบน
- Windows / Python 3.14: รัน `backend/.venv/Scripts/python.exe -m pytest -p no:cacheprovider test -q` จากโฟลเดอร์ backend: **77 passed, 10 subtests passed** ครอบคลุม Login สำเร็จ, รหัสผ่านผิด, status, logout และ API เดิม
- `node --check frontend/public/js/login.js` และ `git diff --check`: ผ่าน
- UI–API ผ่าน browser, Docker และ System Test: ยังไม่รันใน PR นี้
