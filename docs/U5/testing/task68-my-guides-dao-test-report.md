# Task68: U5 — DAO อ่านแนวข้อสอบของผู้ใช้ปัจจุบัน

## ขอบเขตและการออกแบบ

เพิ่ม `MyGuideDAO.list_by_username(username)` เพื่ออ่านแนวข้อสอบของผู้ใช้ที่ผ่านการยืนยันตัวตนแล้ว โดย join `Guide.publisher` และกรองด้วย `User.username` จากนั้น eager-load `Guide.course` เพื่อให้ชั้น API นำข้อมูลรายวิชาไปสร้าง DTO ได้โดยไม่เกิด query เพิ่มหลัง DAO คืนผล รายการเรียงตาม `Guide.id` เพื่อให้ผลลัพธ์แน่นอน

การอ่านไม่มีการเปลี่ยนแปลงข้อมูล และ DAO จะไม่คืนรายการของ publisher คนอื่น แม้รายการนั้นอยู่ในวิชาเดียวกัน ใช้ Entity/ER เดิม `Guide`, `User` และ `Course` ตาม `docs/U3/U3_ DB ER Entity DAO.md` โดยไม่เพิ่มตารางหรือคอลัมน์

## ตารางและ Entity

Task68 ไม่เพิ่ม Entity หรือตาราง ใช้ `Base.metadata.create_all()` ซึ่งสร้างตารางเดิมจากโมเดล `Course`, `User` และ `Guide` ในการตั้งค่าฐานข้อมูลของโปรเจกต์ หากฐานข้อมูลยังไม่มีตาราง ให้ตรวจ `backend/.env` และ `DB_CONNECTION_STRING` ให้ชี้ไปยังฐานข้อมูลที่ถูกต้อง แล้วรันจาก `backend`:

```powershell
python -m app.init_db
```

คำสั่งนี้สร้างตารางที่กำหนดในโมเดลทั้งหมดที่ยังไม่มีอยู่ ไม่ได้สร้างตารางเฉพาะ Task68 และไม่มี migration/schema change ใหม่ในงานนี้

## กรณีทดสอบและผล

ข้อมูลทดสอบสร้างใน schema ชั่วคราวชื่อ `task68_test_<uuid>` บน SQL Server แต่ละกรณีมีผู้ใช้เจ้าของหนึ่งคน ผู้ใช้อื่นหนึ่งคน และแนวข้อสอบหลายรายการในสองรายวิชา รวมข้อมูลภาษาไทย, หัวข้อหลายบรรทัด, nullable fields และรายการของผู้ใช้อื่นในวิชาเดียวกัน ทุก test ใช้ transaction ครอบการสร้าง schema/fixture; cleanup rollback transaction และยืนยันว่า schema ชั่วคราวถูกลบแล้ว จึงไม่ต้องคืนข้อมูลในตารางแอปพลิเคชันหลังทดสอบ

| รหัส | ข้อมูลที่ใช้ | ผลคาดหวัง | ผลจริง SQL Server | ผล SQL Server | หลักฐาน |
|---|---|---|---|---|---|
| T68-DAO01 | `t68_owner` มี 2 รายการต่างวิชา; `t68_other` มี 1 รายการใน CS261 | คืนเฉพาะ 2 รายการของ `t68_owner` เรียงตาม id | ยังรันไม่ได้: environment ไม่มี `backend/.env` และ `DB_CONNECTION_STRING` | ยังไม่ยืนยัน | SQLite: ผ่าน; `test_lists_only_current_username_across_courses_in_id_order` |
| T68-DAO02 | ผู้ใช้ `t68_no_guides` มีอยู่แต่ไม่มี Guide | คืน `[]` | ยังรันไม่ได้: environment ไม่มี `backend/.env` และ `DB_CONNECTION_STRING` | ยังไม่ยืนยัน | SQLite: ผ่าน; `test_returns_empty_list_for_existing_user_without_guides` |
| T68-DAO03 | ค้น username ที่ไม่มีในฐานข้อมูล | คืน `[]` | ยังรันไม่ได้: environment ไม่มี `backend/.env` และ `DB_CONNECTION_STRING` | ยังไม่ยืนยัน | SQLite: ผ่าน; `test_returns_empty_list_for_unknown_username` |
| T68-DAO04 | รายการมี Course relation, ข้อความไทย/หลายบรรทัด และค่า nullable | อ่าน Course ได้หลัง detach Session; ฟิลด์และค่า `NULL` ตรงตาม fixture | ยังรันไม่ได้: environment ไม่มี `backend/.env` และ `DB_CONNECTION_STRING` | ยังไม่ยืนยัน | SQLite: ผ่าน; `test_course_is_eager_loaded_and_nullable_fields_are_preserved` |

รันจากโฟลเดอร์ `backend`:

```powershell
$env:PYTHONPATH='.'
$env:TASK68_TEST_SQLSERVER='1'
.venv\Scripts\python.exe -m unittest discover -s test -p test_my_guide_dao.py -v
Remove-Item Env:TASK68_TEST_SQLSERVER
```

SQLite run: 4 tests passed. SQL Server run: ยังไม่ได้รัน เนื่องจากไม่มี connection configuration ใน environment; ห้ามตีความผล SQLite เป็นผล SQL Server และห้ามระบุ SQL Server ว่าผ่าน หากต้องการรัน SQL Server ให้ตั้ง `DB_CONNECTION_STRING` หรือเตรียม `backend/.env` ในเครื่องก่อน แล้วใช้คำสั่งด้านบน

## การคืนข้อมูลทดสอบ

- SQL Server: suite สร้าง schema แยกต่อ test แล้ว rollback outer transaction, ปิด Session/connection และตรวจ `sys.schemas` ว่า schema ชั่วคราวไม่เหลืออยู่
- SQLite: ใช้ in-memory database ต่อ test และ dispose engine หลัง test จบ
- ไม่ insert, update หรือลบข้อมูลใน schema/tables ของแอปพลิเคชันจริง
- หาก runner ถูกหยุดโดยไม่ทำ cleanup ให้ตรวจ schema ที่ขึ้นต้น `task68_test_` ในฐานข้อมูลทดสอบ และลบเฉพาะ schema ที่ยืนยันว่าเป็นของการทดสอบ Task68
