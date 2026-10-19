# Task60: U4 — รายงานทดสอบ API–DAO การเผยแพร่บน Docker

## ข้อมูลการทดสอบ

| รายการ | รายละเอียด |
|---|---|
| ผู้ทดสอบ | รอระบุ |
| PO | รอระบุ |
| รุ่นโค้ด | `49670bb69e7562d1bc1c52423c6ec5a5698efb95` |
| Database | SQL Server 2022 ใน Docker, database `CS261Group4Dev` |
| API | `POST /guides` และ DAO `PublishGuideDAO.create` |

## กรณีทดสอบ

| รหัส | ข้อมูล | ผลคาดหวัง | ผลจริง/สถานะ | หลักฐาน |
|---|---|---|---|---|
| APIDAO-60-01 | payload ครบ, CS261 มีอยู่, token ถูกต้อง | API ตรวจข้อมูล, DAO สร้าง Guide และ commit ได้ | รอ Docker SQL Server | API response/DB snapshot |
| APIDAO-60-02 | ไม่มี token หรือ token ผิด | HTTP 401 และไม่มี row ใหม่ | รอ Docker SQL Server | status 401/row count |
| APIDAO-60-03 | title/topics ว่าง, count ผิด, field ปลอม | HTTP 422 และ rollback/ไม่มี row ใหม่ | รอ Docker SQL Server | status 422/row count |
| APIDAO-60-04 | course ไม่มีอยู่หรือนอกขอบเขต | HTTP 404 และไม่มี row ใหม่ | รอ Docker SQL Server | status 404/row count |
| APIDAO-60-05 | DAO/Database error ระหว่างบันทึก | HTTP 500 และไม่มีข้อมูลบางส่วนค้าง | รอ Docker SQL Server | log ที่ลบ secret แล้ว |

## ผล Automated Test เดิม

- `test_publish_guide_api.py`: `6 passed, 12 subtests passed`
- `test_publish_guide_dao.py`: `5 passed` ตามรายงาน Task56
- รันทดสอบซ้ำรวมในรอบนี้: `11 passed, 1 warning, 12 subtests passed`
- ชุดเดิมใช้ SQLite หรือ schema ทดสอบ ไม่ใช่ฐาน SQL Server ใน Docker จึงต้องรันซ้ำตามคู่มือ Task60

## สถานะ

ยังไม่ยืนยันผล API–DAO บน Docker เพราะ Docker Engine ยังไม่ทำงานในรอบจัดทำรายงานนี้
