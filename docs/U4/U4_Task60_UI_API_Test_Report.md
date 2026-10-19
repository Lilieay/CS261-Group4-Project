# Task60: U4 — รายงานทดสอบ UI–API การเผยแพร่บน Docker

## ข้อมูลการทดสอบ

| รายการ | รายละเอียด |
|---|---|
| ผู้ทดสอบ | รอระบุ |
| PO | รอระบุ |
| รุ่นโค้ด | `49670bb69e7562d1bc1c52423c6ec5a5698efb95` |
| สภาพแวดล้อม | Windows, Docker Compose, SQL Server 2022, Frontend `:5000`, Backend `:8000` |
| โหมด TU | `mock` สำหรับการทดสอบในเครื่อง; ห้ามใส่ key จริงในรายงาน |

## ขอบเขต

ทดสอบหน้า `upload.html` ส่งข้อมูลไป `POST /guides` แล้วตรวจ response, การแสดงข้อความสำเร็จ/ผิดพลาด และลิงก์ไปหน้าอ่านแนวข้อสอบ โดยใช้ token จาก Login เดิม

## กรณีทดสอบ

| รหัส | ข้อมูล | ผลคาดหวัง | ผลจริง/สถานะ | หลักฐาน |
|---|---|---|---|---|
| UIAPI-60-01 | Login แล้วกรอก CS261 ครบ | หน้าเว็บส่ง Bearer token, API ตอบ 201 และเปิดรายละเอียดได้ | รอ Docker/Browser | ภาพหน้าจอและ status ที่ปิด token |
| UIAPI-60-02 | เว้นชื่อ/หัวข้อ/ข้อมูลบังคับ | หน้าแจ้งช่องที่ผิด และไม่ส่ง/ไม่สร้างรายการ | รอ Docker/Browser | ภาพ validation |
| UIAPI-60-03 | จำนวนข้อเป็น 0, ติดลบ หรือทศนิยม | หน้า/API ปฏิเสธข้อมูล และข้อมูลเดิมไม่เปลี่ยน | รอ Docker/Browser | response ที่ลบข้อมูลลับ |
| UIAPI-60-04 | ไม่มี token หรือ token หมดอายุ | API ตอบ 401 และหน้าแจ้งให้ Login ใหม่ | รอ Docker/Browser | status 401 |
| UIAPI-60-05 | Backend ใช้งานไม่ได้ | หน้าแจ้งบันทึกไม่สำเร็จและไม่แสดงว่าสำเร็จ | รอ Docker/Browser | ภาพ error |

## ผลที่มีอยู่ก่อนรวม Docker

- API Test ของ Task57: `6 passed, 12 subtests passed` ด้วย SQLite/TestClient
- DAO Test ของ Task56: `5 passed` ในชุดทดสอบที่รายงานไว้
- รันทดสอบซ้ำในรอบนี้ด้วย SQLite: `11 passed, 1 warning, 12 subtests passed`
- ผลข้างต้นยืนยัน component flow แต่ยังไม่ใช่ UI–API บน Docker

## สถานะ

Docker Engine ยังไม่พร้อมในรอบจัดทำรายงาน (`docker info` ติดต่อ Docker Desktop ไม่ได้) จึงยังไม่สรุปว่า UI–API บน Docker ผ่าน ต้องกรอกผลจริงและหลักฐานหลังเปิด Docker แล้ว
