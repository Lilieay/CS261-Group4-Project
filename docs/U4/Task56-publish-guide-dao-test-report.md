# Task56: U4 — DAO บันทึกแนวข้อสอบใหม่

## ขอบเขตและการออกแบบ

เพิ่ม `PublishGuideDAO.create(guide)` สำหรับบันทึก Entity `Guide` ตามโครงสร้างเดิมใน `guides` โดย DAO เรียก `Session.add()` และ `Session.flush()` เพื่อให้ฐานข้อมูลสร้าง `id` แล้วคืน Entity กลับไป DAO ไม่เรียก `commit()` หรือ `rollback()` เอง ให้ Service/ผู้เรียกเป็นผู้ควบคุม transaction ตามสัญญาใน Task52

Task นี้ไม่เพิ่ม Entity, ตาราง, คอลัมน์ หรือความสัมพันธ์ใหม่ ตาราง `guides` ใช้ Foreign Key เดิมไปยัง `courses.id` และ `users.id`; ผู้เรียกต้องส่ง `course_id` ที่ตรวจสอบแล้วและ `publisher_id` ที่ได้จากผู้ใช้ปัจจุบัน ไม่ควรรับเจ้าของจาก request โดยตรง

## วิธีสร้างตาราง

ไม่ต้องสร้างตารางใหม่สำหรับ Task56 เพราะ Entity `Guide` และการ import ใน `backend/app/init_db.py` มีอยู่แล้ว หาก clone ฐานข้อมูลที่ยังไม่มี schema ให้ตั้ง `DB_CONNECTION_STRING` ใน `backend/.env` แล้วรันจาก `backend`:

```powershell
python -m app.init_db
```

คำสั่งนี้ใช้ `Base.metadata.create_all()` และสร้างตารางที่ประกาศใน Entity ที่ import ไว้ หากอนาคตเพิ่ม Entity/ตารางใหม่ ให้ import Entity นั้นใน `backend/app/init_db.py` ก่อนรันคำสั่งเดิม ทั้งนี้ `create_all()` ไม่ได้ใช้แทน migration สำหรับแก้ schema ของตารางที่มีอยู่แล้ว

## วิธีทดสอบและคืนข้อมูล

รันทดสอบจาก `backend`:

```powershell
python -m pytest test/test_publish_guide_dao.py -q
```

ค่าเริ่มต้นทดสอบด้วย SQLite ชั่วคราวและเปิด Foreign Key enforcement ส่วนทดสอบ SQL Server ใช้ schema แยกชื่อ `task56_test_<uuid>`:

```powershell
$env:TASK56_TEST_SQLSERVER="1"
python -m pytest test/test_publish_guide_dao.py -q
Remove-Item Env:TASK56_TEST_SQLSERVER
```

ข้อมูลทดสอบทั้งหมดอยู่ใน transaction ของ test; teardown rollback transaction และสำหรับ SQL Server ตรวจ `sys.schemas` ว่า schema ชั่วคราวไม่เหลืออยู่ จึงไม่ต้องลบข้อมูลในฐานข้อมูลจริงด้วยมือ ห้ามตั้ง `TASK56_TEST_SQLSERVER=1` หาก `DB_CONNECTION_STRING` ไม่ได้ชี้ไปยังฐานทดสอบที่ได้รับอนุญาต

## รายงานผลการทดสอบ

| รหัส | ข้อมูลทดสอบ | ผลคาดหวัง | ผลจริง | ผ่าน/ไม่ผ่าน | หลักฐาน |
|---|---|---|---|---|---|
| T56-DAO01 | Guide ใหม่ครบฟิลด์ อ้างอิง Course และ User ที่มีอยู่ | บันทึกได้ คืน Entity เดิมพร้อม ID และค่าฟิลด์/เจ้าของถูกต้อง | SQLite: ได้ ID และค่าที่อ่านกลับตรงตามที่ส่ง; SQL Server: ยังไม่ได้รันเพราะไม่มี DB config | ผ่าน (SQLite); SQL Server ยังไม่ทดสอบ | `test_create_persists_guide_and_returns_generated_id` |
| T56-DAO02 | เว้นจำนวนข้อทั้งสองและคำแนะนำเป็น `NULL` | บันทึกได้ และค่าที่ไม่ระบุยังเป็น `NULL` | SQLite: ค่าทั้งสามยังเป็น `NULL`; SQL Server: ยังไม่ได้รันเพราะไม่มี DB config | ผ่าน (SQLite); SQL Server ยังไม่ทดสอบ | `test_create_preserves_nullable_optional_fields` |
| T56-DAO03 | บันทึกสองรายการชื่อเดียวกันแต่คนละปี | ทั้งสองรายการถูกบันทึกด้วย ID ต่างกัน เพราะชื่อไม่ unique | SQLite: สร้างได้ 2 รายการและ ID ต่างกัน; SQL Server: ยังไม่ได้รันเพราะไม่มี DB config | ผ่าน (SQLite); SQL Server ยังไม่ทดสอบ | `test_create_allows_same_title_for_separate_records` |
| T56-DAO04 | สร้างรายการภายใน savepoint แล้ว rollback | DAO ไม่ commit; rollback แล้วไม่พบรายการ | SQLite: rollback แล้วไม่พบรายการ; SQL Server: ยังไม่ได้รันเพราะไม่มี DB config | ผ่าน (SQLite); SQL Server ยังไม่ทดสอบ | `test_create_does_not_commit_callers_transaction` |
| T56-DAO05 | ใช้ `course_id` ที่ไม่มีอยู่ | ฐานข้อมูลปฏิเสธ Foreign Key และไม่มีรายการบางส่วน | SQLite: เกิด `IntegrityError` และไม่มีรายการ; SQL Server: ยังไม่ได้รันเพราะไม่มี DB config | ผ่าน (SQLite); SQL Server ยังไม่ทดสอบ | `test_invalid_foreign_key_is_rejected_without_partial_record` |

**ผลรันจริง:** SQLite `5 passed` ด้วยคำสั่งข้างต้น (`backend/.venv/Scripts/python.exe -m pytest test/test_publish_guide_dao.py -q`). ยังไม่ได้ทดสอบ SQL Server เพราะ checkout นี้ไม่มี `backend/.env` และไม่มี `DB_CONNECTION_STRING` ใน environment; ไม่ได้เชื่อมต่อฐานข้อมูลจริงโดยไม่ได้รับการยืนยันว่าเป็นฐานทดสอบ

ผล SQLite และ SQL Server จะบันทึกแยกตาม environment หลังจากรันจริง; ห้ามระบุว่าผ่าน SQL Server หากยังไม่ได้เชื่อมต่อและรันทดสอบบนฐาน SQL Server
