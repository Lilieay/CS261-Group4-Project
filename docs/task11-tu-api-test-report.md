# Task11: รายงานทดสอบการยืนยันบัญชีกับ TU API

## API ที่ทำ

```text
POST /api/auth/verify-tu
```

Backend รับ `username` และ `password` แล้วเรียก service กลาง `verify_with_tu_api` ผลลัพธ์ที่ส่งกลับมี `verified`, `message` และ `source`

## โหมดการทำงาน

- `TU_API_MODE=mock`: ใช้ผลจำลองสำหรับพัฒนาและทดสอบ โดยไม่ส่งข้อมูลออกไปภายนอก
- `TU_API_MODE=real`: เรียก URL จาก `TU_API_URL` และส่ง API key จาก `TU_API_KEY` ถ้ามีการตั้งค่า

ยังไม่ควรใส่ password, API key หรือ token จริงในไฟล์นี้หรือใน GitHub

## ผลทดสอบ Mock

| กรณี | ข้อมูลทดสอบ | ผลที่คาดหวัง | ผลจริง | สถานะ | หลักฐาน |
|---|---|---|---|---|---|
| ข้อมูลถูกต้อง | ค่า `TU_MOCK_USERNAME` / `TU_MOCK_PASSWORD` ใน environment | HTTP 200 และ `verified=true` | กรอกหลังรัน Postman | รอทดสอบ | แนบภาพ Postman |
| ข้อมูลผิด | `wrong_user` / `wrong_password` | HTTP 200 และ `verified=false` | กรอกหลังรัน Postman | รอทดสอบ | แนบภาพ Postman |
| ข้อมูลไม่ครบ | ไม่ส่ง password | HTTP 422 | กรอกหลังรัน Postman | รอทดสอบ | แนบภาพ Postman |

## ผลทดสอบ TU API จริง

ให้กรอกส่วนนี้เมื่อได้รับ endpoint และบัญชีทดสอบจากทีม TU แล้วเท่านั้น โดยระบุ `source=tu_api` และไม่แนบข้อมูลลับในภาพหลักฐาน

| กรณี | ผลที่คาดหวัง | ผลจริง | สถานะ | หลักฐาน |
|---|---|---|---|---|
| บัญชี TU ถูกต้อง | `verified=true` | รอทดสอบ | รอทดสอบ | แนบภาพที่ปิดข้อมูลลับแล้ว |
| บัญชี TU ไม่ถูกต้อง | `verified=false` หรือ HTTP 401 | รอทดสอบ | รอทดสอบ | แนบภาพที่ปิดข้อมูลลับแล้ว |
| TU API ใช้งานไม่ได้ | ได้ข้อความเชื่อมต่อไม่ได้ | รอทดสอบ | รอทดสอบ | แนบ response/log ที่ไม่เปิดเผย secret |
