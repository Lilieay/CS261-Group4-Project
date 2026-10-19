# Task60: U4 — รายงานทดสอบ API–DAO การเผยแพร่บน Docker

## ข้อมูลการทดสอบ

| รายการ | รายละเอียด |
|---|---|
| รุ่นโค้ด | 6efc76d บน branch feat/task60-publish-api-docker |
| Database | SQL Server 2022 ใน Docker, database CS261Group4Dev |
| Compose project / volume | cs261-task60-test / cs261-task60-test_sqlserver_data |
| API / DAO | POST /guides, PublishGuideService, PublishGuideDAO.create |

## ผลทดสอบ

| รหัส | กรณี | ผลจริง/สถานะ | หลักฐาน |
|---|---|---|---|
| APIDAO-60-01 | payload ถูกต้อง, CS261 มีอยู่, token ใช้ได้ | ผ่าน: API ตอบ 201; อ่านรายละเอียดกลับด้วย 200 | browser flow; guide ID 5 |
| APIDAO-60-02 | ไม่มี token | ผ่าน: API ตอบ 401 AUTH_REQUIRED | POST ผ่าน /api/guides |
| APIDAO-60-03 | title มีแต่ช่องว่าง | ผ่าน: API ตอบ 422 INVALID_PARAMETERS, field title | POST ผ่าน /api/guides |
| APIDAO-60-04 | ยืนยันข้อมูลที่บันทึกและจำนวนครั้ง | ผ่าน: SQL Server อ่าน guide ID 5, course ID 4, publisher ID 2, ปี 2568, ภาคเรียน 1, midterm, objective_count=20; มี 5 แถวรวม (seed 4 + รายการทดสอบ 1) หลังคำขอ 401/422 | SQL query บน cs261-task60-test_sqlserver_data |
| APIDAO-60-05 | Database error ระหว่างบันทึก | ยังไม่ได้จำลอง | — |

## ขอบเขตของผล

การทดสอบนี้ยืนยันการเขียนและอ่านข้อมูลจริงบน SQL Server ใน volume ทดสอบแยก การทดสอบ DAO/API แบบ SQLite จาก Task56/57 เป็นหลักฐานเดิมในรายงานของงานเหล่านั้น และไม่ได้รันซ้ำในรอบนี้ การตรวจ rollback เมื่อ SQL Server error และการทดสอบด้วยบัญชีผู้เผยแพร่คนที่สองยังไม่ได้ทำ
