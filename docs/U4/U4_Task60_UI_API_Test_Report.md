# Task60: U4 — รายงานทดสอบ UI–API การเผยแพร่บน Docker

## ข้อมูลการทดสอบ

| รายการ | รายละเอียด |
|---|---|
| ผู้ทดสอบ | รอระบุ |
| PO | รอระบุ |
| รุ่นโค้ด | `7bc35a759028d7b21d85dfa7504ce0995169ddd7` |
| สภาพแวดล้อม | Windows, Docker Compose, SQL Server 2022, Frontend `:5000`, Backend `:8000` |
| โหมด TU | `mock` สำหรับการทดสอบในเครื่อง; ห้ามใส่ key จริงในรายงาน |

## ขอบเขต

ทดสอบหน้า `upload.html` ส่งข้อมูลไป `POST /guides` แล้วตรวจ response, การแสดงข้อความสำเร็จ/ผิดพลาด และลิงก์ไปหน้าอ่านแนวข้อสอบ โดยใช้ token จาก Login เดิม

## กรณีทดสอบ

| รหัส | ข้อมูล | ผลคาดหวัง | ผลจริง/สถานะ | หลักฐาน |
|---|---|---|---|---|
| UIAPI-60-01 | เปิด Login และ Upload ผ่าน Frontend Docker | หน้าเว็บตอบ `200`; API smoke flow Login → Publish → Read ตอบ `200/201/200` | ผ่าน | HTTP status ที่ตรวจใน Docker |
| UIAPI-60-02 | เว้นชื่อ/หัวข้อ/ข้อมูลบังคับ | API ปฏิเสธข้อมูลไม่ถูกต้อง | รอ Browser UAT | ต้องแนบภาพ validation |
| UIAPI-60-03 | จำนวนข้อเป็น 0, ติดลบ หรือทศนิยม | API ปฏิเสธข้อมูล และข้อมูลเดิมไม่เปลี่ยน | รอ Browser UAT | ต้องแนบ response ที่ลบข้อมูลลับ |
| UIAPI-60-04 | ไม่มี token | API ตอบ `401` และไม่สร้างรายการ | ผ่าน | `POST /guides` ได้ `401` |
| UIAPI-60-05 | Backend ใช้งานไม่ได้ | หน้าแจ้งบันทึกไม่สำเร็จ | รอ Browser UAT | ต้องแนบภาพ error |

## ผลที่มีอยู่ก่อนรวม Docker

- API Test ของ Task57: `6 passed, 12 subtests passed` ด้วย SQLite/TestClient
- DAO Test ของ Task56: `5 passed` ในชุดทดสอบที่รายงานไว้
- รันทดสอบซ้ำในรอบนี้ด้วย SQLite: `11 passed, 1 warning, 12 subtests passed`
- Docker smoke test: Login `200`, Course `200`, Publish `201`, Read `200`, List `200`, Unauthorized `401`, Delete ข้อมูลทดสอบ `200`
- เปิด `login.html` และ `upload.html` จาก Frontend container ได้ `200`
- Smoke test ใช้ Backend container ชั่วคราวโหมด `mock`; ไม่ใช้ TU key จริง และลบข้อมูลทดสอบแล้ว

## สถานะ

โครงสร้าง Docker และ API smoke flow ผ่านแล้ว เหลือ Browser UAT สำหรับ validation/error และ PO ตรวจรับ
