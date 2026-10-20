# Task69: U5 — DAO แก้ไขและย้ายวิชาแนวข้อสอบ

## DAO และ Entity ที่เกี่ยวข้อง

เพิ่ม `UpdateOwnedGuideDAO.update_owned(guide_id, publisher_id, payload)` สำหรับ update แถว `Guide` เดิม โดย SQL มีเงื่อนไขทั้ง `guides.id` และ `guides.publisher_id` หากไม่พบรายการหรือเจ้าของไม่ตรง คืน `None`; หากแก้ได้หนึ่งแถว คืน `Guide` พร้อม `Course` ที่โหลดแล้ว DAO ไม่ commit เอง เพื่อให้ API เป็นผู้ควบคุม transaction

DAO อนุญาตเฉพาะฟิลด์แก้ไขตาม U5 ได้แก่ `course_id`, `title`, `academic_year`, `semester`, `exam_period`, `topics`, `exam_format`, จำนวนข้อ และ `additional_advice` ปฏิเสธ `publisher_id` และฟิลด์อื่นที่ไม่ได้อยู่ในรายการแก้ไข การย้ายวิชาเปลี่ยน `course_id` ของ row เดิม โดยคง `Guide.id` และ `publisher_id`

ใช้ Entity/ER เดิม `Guide`, `Course` และ `User` ตาม `docs/U3/U3_ DB ER Entity DAO.md`; ไม่เพิ่มหรือแก้ Entity, ตาราง, column หรือ relationship จึงไม่มี DDL ใหม่ หากฐานข้อมูลที่ถูกต้องยังไม่มีตารางเดิม ให้ใช้ `python -m app.init_db` จาก `backend` หลังตั้ง `DB_CONNECTION_STRING` ใน `backend/.env`; คำสั่งนี้สร้างตารางตามโมเดลเดิม ไม่ใช่ migration ของ Task69

## Test setup และการคืนข้อมูล

ข้อมูลทดสอบมีเจ้าของ `t69_owner`, ผู้ใช้อื่น `t69_other`, รายวิชา CS261/CS262, รายการของเจ้าของ 2 รายการ และรายการของผู้ใช้อื่น 1 รายการ แต่ละ SQL Server test สร้าง schema `task69_test_<uuid>` และตารางจาก Entity ภายใน outer transaction เมื่อจบ test ปิด Session, rollback transaction และตรวจ `sys.schemas` ว่าไม่มี schema ทดสอบค้าง ข้อมูลในตารางแอปจริงไม่ถูกแก้ SQLite ใช้ in-memory database และ dispose เมื่อจบ test

## ผลทดสอบ

| รหัส | ข้อมูลทดสอบ | ผลคาดหวัง | ผลจริง SQL Server | สถานะ SQL Server | หลักฐาน SQLite |
|---|---|---|---|---|---|
| T69-DAO01 | เจ้าของแก้ชื่อ/เนื้อหาและย้ายรายการ CS261 ไป CS262 | คืน Guide เดิม โดย ID/เจ้าของคงเดิม, course และฟิลด์เปลี่ยนตาม payload, ไม่มี row ซ้ำ | ยังรันไม่ได้: ไม่มี `backend/.env` หรือ `DB_CONNECTION_STRING` ใน environment | ยังไม่ทดสอบ | Pass — `test_update_owned_guide_and_move_it_to_another_course` |
| T69-DAO02 | ส่ง publisher ID ของผู้ใช้อื่นให้รายการเจ้าของ | คืน `None`; ทุกฟิลด์เดิมคงเดิม | ยังรันไม่ได้: ไม่มี connection config | ยังไม่ทดสอบ | Pass — `test_non_owner_update_returns_none_and_changes_nothing` |
| T69-DAO03 | ส่ง guide ID ที่ไม่มีอยู่ | คืน `None`; จำนวนรายการไม่เปลี่ยน | ยังรันไม่ได้: ไม่มี connection config | ยังไม่ทดสอบ | Pass — `test_missing_guide_returns_none_and_changes_nothing` |
| T69-DAO04 | payload พยายามแก้ `publisher_id` หรือส่ง payload ว่าง | ปฏิเสธด้วย `ValueError`; ข้อมูลเดิมคงเดิม | ยังรันไม่ได้: ไม่มี connection config | ยังไม่ทดสอบ | Pass — `test_cannot_update_owner_or_unknown_fields` |

SQLite: รัน 4 tests — `OK`. ผล SQLite ไม่ใช่ผลยืนยัน SQL Server; สถานะ SQL Server จึงคงเป็น “ยังไม่ทดสอบ” จนกว่าจะมี connection configuration

รันจาก `backend` บน SQLite (placeholder นี้ใช้เพียงให้ module config ผ่าน import; test ใช้ SQLite in-memory):

```powershell
$env:DB_CONNECTION_STRING='DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=unused;Trusted_Connection=yes;TrustServerCertificate=yes'
$env:PYTHONPATH='.'
.venv\Scripts\python.exe -m unittest discover -s test -p test_update_owned_guide_dao.py -v
Remove-Item Env:DB_CONNECTION_STRING
Remove-Item Env:PYTHONPATH
```

เมื่อมี SQL Server connection ใน `backend/.env` ให้รัน:

```powershell
$env:PYTHONPATH='.'
$env:TASK69_TEST_SQLSERVER='1'
.venv\Scripts\python.exe -m unittest discover -s test -p test_update_owned_guide_dao.py -v
Remove-Item Env:TASK69_TEST_SQLSERVER
Remove-Item Env:PYTHONPATH
```
