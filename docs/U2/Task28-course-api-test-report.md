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
| COURSE-API-01 | Login ด้วยบัญชีที่ถูกต้อง แล้ว `GET /courses` | HTTP 200 และทุกรายการเป็นรหัส `CS` | `<บันทึกผลจากการรันจริง>` | `<ผ่าน/ไม่ผ่าน/รอทดสอบ>` | `<Postman หรือ pytest>` |
| COURSE-API-02 | `GET /courses?search=CS261` | HTTP 200 และคืนรายการที่รหัสตรงคำค้น | `<บันทึกผลจากการรันจริง>` | `<ผ่าน/ไม่ผ่าน/รอทดสอบ>` | `<Postman หรือ pytest>` |
| COURSE-API-03 | `GET /courses?search=software` | HTTP 200 และค้นจากชื่อรายวิชาได้ | `<บันทึกผลจากการรันจริง>` | `<ผ่าน/ไม่ผ่าน/รอทดสอบ>` | `<Postman หรือ pytest>` |
| COURSE-API-04 | `GET /courses/{course_id}` ของรายวิชาที่มีอยู่ | HTTP 200 และฟิลด์ DTO ครบ | `<บันทึกผลจากการรันจริง>` | `<ผ่าน/ไม่ผ่าน/รอทดสอบ>` | `<Postman หรือ pytest>` |
| COURSE-API-05 | `GET /courses/999` | HTTP 404 พร้อม `COURSE_NOT_FOUND` | `<บันทึกผลจากการรันจริง>` | `<ผ่าน/ไม่ผ่าน/รอทดสอบ>` | `<Postman หรือ pytest>` |
| COURSE-API-06 | เรียก `/courses` โดยไม่ส่ง Authorization | HTTP 401 พร้อม `AUTH_REQUIRED` | `<บันทึกผลจากการรันจริง>` | `<ผ่าน/ไม่ผ่าน/รอทดสอบ>` | `<Postman หรือ pytest>` |

## Postman และข้อมูลที่ใช้

ใช้ `Task28-course-api.postman_collection.json` โดยต้องกรอก password ใน Environment ของผู้ทดสอบเองก่อนรัน Login Collection ไม่เก็บ password จริงหรือ token จริงไว้ในไฟล์ Collection

ค่าตัวอย่างที่ใช้ทดสอบ:

- `base_url`: `http://127.0.0.1:8000`
- `username`: `student`
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
- ต้องรัน Postman หรือ pytest ใน environment ที่ติดตั้ง dependencies และมีฐานข้อมูล/seed data ก่อนกรอกผลจริงในตาราง
- รายงานนี้ระบุผลคาดหวังและโครงสร้างหลักฐาน แต่ไม่อ้างว่าเป็นผล Demo จริงจนกว่าจะมีการรันและบันทึกหลักฐาน
