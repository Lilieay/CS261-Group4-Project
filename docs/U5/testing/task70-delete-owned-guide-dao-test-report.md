# Task70: U5 — DAO ลบแนวข้อสอบของเจ้าของ

## ขอบเขตและการออกแบบ

เพิ่ม `DeleteOwnedGuideDAO.delete_owned(guide_id, publisher_id)` สำหรับลบแนวข้อสอบหนึ่งรายการ โดย DAO ใส่ทั้ง `guides.id` และ `guides.publisher_id` ในเงื่อนไข `DELETE` เดียวกัน จึงไม่ลบรายการของผู้ใช้อื่น และไม่ต้องอ่านข้อมูลก่อนลบ การคืนค่าเป็น `True` เมื่อกระทบหนึ่งแถว และ `False` เมื่อไม่พบรายการหรือผู้เรียกไม่ใช่เจ้าของ

ใช้ Entity `Guide` ที่มีอยู่แล้ว ตาราง `guides` อ้างอิง `courses.id` และ `users.id` ด้วย Foreign Key ตามแบบจำลองปัจจุบัน ไม่ต้องเพิ่มตารางหรือเปลี่ยน schema สำหรับ Task70

## การสร้างตาราง

`db/init.sql` ใช้สร้างฐานข้อมูล `CS261Group4Dev` เท่านั้น ตารางของ Entity ถูกสร้างด้วย SQLAlchemy ใน `backend/app/init_db.py` ผ่าน `Base.metadata.create_all(bind=engine)`. เมื่อเพิ่ม Entity/table ใหม่ในอนาคต:

1. เพิ่ม model ใน `backend/app/models/` และกำหนด `__tablename__`, columns, constraints และ Foreign Keys
2. import model ใหม่ใน `backend/app/init_db.py` เพื่อให้ SQLAlchemy ลงทะเบียนตารางกับ `Base.metadata`
3. ตั้งค่า `DB_CONNECTION_STRING` ใน `backend/.env` ตาม `backend/app/config.py`
4. จากโฟลเดอร์ `backend` รัน `python -m app.init_db`

`create_all` สร้างตารางที่ยังไม่มี แต่ไม่ทำ migration ให้ตารางที่มีอยู่แล้ว หากแก้ schema ของตารางเดิม ต้องจัดทำและรัน migration/DDL ที่เหมาะสมแยกต่างหาก

## ข้อมูลทดสอบและการคืนข้อมูล

แต่ละกรณีสร้าง schema ชั่วคราว `task70_test_<uuid>` บน SQL Server หรือฐานข้อมูล SQLite ในหน่วยความจำ สร้างผู้ใช้เจ้าของหนึ่งราย ผู้ใช้อื่นหนึ่งราย วิชา CS261 หนึ่งวิชา และแนวข้อสอบสามรายการ (ของเจ้าของสองรายการและของผู้ใช้อื่นหนึ่งรายการ)

Session ใช้ `join_transaction_mode="rollback_only"` ภายใน transaction ครอบนอก หลังแต่ละกรณีปิด Session แล้ว rollback transaction เพื่อคืนข้อมูลทั้งหมดและ schema ชั่วคราว; suite ตรวจสอบว่า schema ไม่เหลืออยู่ใน `sys.schemas`. SQLite ในหน่วยความจำถูกทิ้งเมื่อจบกรณี จึงไม่แตะข้อมูลฐานข้อมูลจริง

## Test cases และผล

| รหัส | ข้อมูล/การทำงาน | ผลคาดหวัง | ผลจริง SQL Server | SQL Server | ผลจริง SQLite | SQLite |
|---|---|---|---|---|---|---|
| T70-DAO01 | ลบ ID ของรายการเจ้าของด้วย publisher ID ที่ตรงกัน | คืน `True`; ลบรายการเป้าหมายรายการเดียว | เริ่มเชื่อมต่อไม่สำเร็จ ก่อนเข้า DAO: ODBC `IM002`, ไม่พบ DSN/driver | ไม่ได้รัน | คืน `True`; คงเหลืออีกสองรายการ | ผ่าน |
| T70-DAO02 | ใช้ publisher ID ของเจ้าของกับรายการของผู้ใช้อื่น | คืน `False`; รายการทั้งสามยังอยู่ | เริ่มเชื่อมต่อไม่สำเร็จ ก่อนเข้า DAO: ODBC `IM002`, ไม่พบ DSN/driver | ไม่ได้รัน | คืน `False`; รายการทั้งสามยังอยู่ | ผ่าน |
| T70-DAO03 | ลบ ID ที่ไม่มีอยู่ (`-1`) | คืน `False`; ข้อมูลทั้งหมดยังคงเดิม | เริ่มเชื่อมต่อไม่สำเร็จ ก่อนเข้า DAO: ODBC `IM002`, ไม่พบ DSN/driver | ไม่ได้รัน | คืน `False`; รายการทั้งสามยังอยู่ | ผ่าน |
| T70-DAO04 | ลบรายการของเจ้าของหนึ่งรายการซึ่งมีอีกรายการของเจ้าของและผู้ใช้อื่นอยู่ | ลบเฉพาะเป้าหมาย; อีกสองรายการคงอยู่ | เริ่มเชื่อมต่อไม่สำเร็จ ก่อนเข้า DAO: ODBC `IM002`, ไม่พบ DSN/driver | ไม่ได้รัน | คงเหลือเฉพาะอีกรายการเจ้าของและรายการผู้ใช้อื่น | ผ่าน |
| T70-DAO05 | ลบรายการเดิมซ้ำสองครั้ง | ครั้งแรกคืน `True`, ครั้งที่สองคืน `False` | เริ่มเชื่อมต่อไม่สำเร็จ ก่อนเข้า DAO: ODBC `IM002`, ไม่พบ DSN/driver | ไม่ได้รัน | ครั้งแรก `True`; ครั้งที่สอง `False` | ผ่าน |

## วิธีรันทดสอบ

จากโฟลเดอร์ `backend`:

```powershell
$env:PYTHONPATH='.'
Remove-Item Env:TASK70_TEST_SQLSERVER -ErrorAction SilentlyContinue
.venv\Scripts\python.exe -m unittest discover -s test -p test_delete_owned_guide_dao.py -v
```

สำหรับ SQL Server ที่เข้าถึง credentials ตามการตั้งค่าของแอปได้:

```powershell
$env:PYTHONPATH='.'
$env:TASK70_TEST_SQLSERVER='1'
.venv\Scripts\python.exe -m unittest discover -s test -p test_delete_owned_guide_dao.py -v
```

## ผลการรันใน environment นี้

```text
SQLite:     Ran 5 tests in 0.037s — OK
SQL Server: ไม่สามารถเริ่มทดสอบได้; pyodbc คืน IM002 เพราะไม่พบ ODBC Driver/DSN
```

SQL Server ทั้งห้ากรณีจึงยังไม่มีผล Pass/Fail ของ DAO; ความล้มเหลวเกิดตอนเปิด connection ใน `setUp` ก่อนสร้าง schema หรือเรียก DAO ไม่ใช่ผลทดสอบ assertion. ต้องติดตั้ง/เปิดใช้ ODBC Driver 18 และ SQL Server instance ที่ `backend/.env.example` ระบุ (`.\SQLEXPRESS`) แล้วรันคำสั่ง SQL Server ซ้ำเพื่อเติมผลจริง
