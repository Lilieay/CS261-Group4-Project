# Task60: U4 — รายงานทดสอบ API–DAO การเผยแพร่บน Docker

## ข้อมูลการทดสอบ

| รายการ | รายละเอียด |
|---|---|
| ผู้ทดสอบ | รอระบุ |
| PO | รอระบุ |
| รุ่นโค้ด | `7bc35a759028d7b21d85dfa7504ce0995169ddd7` |
| Database | SQL Server 2022 ใน Docker, database `CS261Group4Dev` |
| API | `POST /guides` และ DAO `PublishGuideDAO.create` |

## กรณีทดสอบ

| รหัส | ข้อมูล | ผลคาดหวัง | ผลจริง/สถานะ | หลักฐาน |
|---|---|---|---|---|
| APIDAO-60-01 | payload ครบ, CS261 มีอยู่, token ถูกต้อง | API ตรวจข้อมูล, DAO สร้าง Guide และ commit ได้ | ผ่าน: `201` และอ่านรายการกลับได้ `200` | Docker smoke output |
| APIDAO-60-02 | ไม่มี token หรือ token ผิด | HTTP 401 และไม่มี row ใหม่ | ผ่าน: `401` | Docker smoke output |
| APIDAO-60-03 | title/topics ว่าง, count ผิด, field ปลอม | HTTP 422 และ rollback/ไม่มี row ใหม่ | ผ่านใน automated component tests | `11 passed, 1 warning, 12 subtests` |
| APIDAO-60-04 | course ไม่มีอยู่หรือนอกขอบเขต | HTTP 404 และไม่มี row ใหม่ | ผ่านใน automated component tests | `test_publish_guide_api.py` |
| APIDAO-60-05 | DAO/Database error ระหว่างบันทึก | HTTP 500 และไม่มีข้อมูลบางส่วนค้าง | รอทดสอบจำลอง DB error | log ที่ลบ secret แล้ว |

## ผล Automated Test เดิม

- `test_publish_guide_api.py`: `6 passed, 12 subtests passed`
- `test_publish_guide_dao.py`: `5 passed` ตามรายงาน Task56
- รันทดสอบซ้ำรวมในรอบนี้: `11 passed, 1 warning, 12 subtests passed`
- Docker smoke test กับ SQL Server ที่รันอยู่ผ่าน Compose: publish `201`, read `200`, list `200`; ข้อมูลชั่วคราวถูกลบหลังทดสอบ

## สถานะ

ยืนยันเส้นทาง API–DAO หลักบน Docker แล้ว เหลือกรณีจำลอง database error และ PO ตรวจรับ
