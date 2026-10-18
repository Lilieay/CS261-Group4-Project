# Task41: ชุดข้อมูล Seed สำหรับหน้าอ่านแนวข้อสอบ

## โครงสร้างไฟล์

```text
backend/
  scripts/
    seed_guides.py                 # CLI, transaction และผลลัพธ์
    seed_data/
      guide_seed_service.py        # จัดการข้อมูลผ่าน SQLAlchemy Session
      datasets/
        test.json                  # ข้อมูลสำหรับกรณีทดสอบ
        demo.json                  # ข้อมูลสำหรับสาธิต
  test/
    test_guide_seed_service.py     # ตรวจการรันซ้ำ, rollback และขอบเขตการลบ
docs/
  U3/
    Task41-guide-seed-data.md      # วิธีใช้และผลตรวจ
```

ชุดทดสอบกับชุด Demo ใช้ข้อมูลและ publisher คนละชุด แต่ใช้ Service เดียวกัน

| ส่วน | หน้าที่ |
|---|---|
| `seed_guides.main()` | อ่าน argument, เปิด Session/transaction, เรียก Service และแสดงผลหลัง commit สำเร็จ |
| `GuideSeedService.seed()` | เพิ่มหรือปรับข้อมูลตาม dataset แล้ว flush โดยไม่ commit |
| `GuideSeedService.verify()` | ตรวจข้อมูล publisher และแนวข้อสอบกับ JSON แล้วคืนจำนวนรายการ Seed แยกตามวิชา |
| `GuideSeedService.restore()` | ลบรายการของ dataset และ publisher ที่ไม่มีรายการอื่นอ้างถึง แล้วคืนจำนวนรายการที่ลบจริง |
| `datasets/*.json` | เก็บข้อมูลตั้งต้น แยกออกจากโค้ดจัดการฐานข้อมูล |

CLI ใช้ `SessionLocal.begin()` คุม transaction ครอบทั้ง `seed()` และ `verify()` หากตรวจไม่ผ่านจะ rollback ทั้งชุด Service รับ Session จากผู้เรียก จึงนำไปใช้ในชุดทดสอบได้โดยไม่เปิดการเชื่อมต่อหรือ commit เอง และไม่ต้องเพิ่ม Router หรือ API สำหรับ Seed

## ข้อมูลในแต่ละชุด

### Test

- CS261 มีรายการหลายปี ภาคเรียน และช่วงสอบ ครอบคลุมตัวกรองเดี่ยวและหลายตัวกรอง
- มีรายการ CS261 ที่ตรงกับ `2568 / 1 / midterm` ครบ และรายการที่ตรงเพียงบางเงื่อนไข
- CS102 มีรายการที่ใช้เงื่อนไขเดียวกับ CS261 เพื่อตรวจการแยกรายวิชา
- มีหัวข้อหลายบรรทัด, รูปแบบข้อสอบครบทั้ง `objective`, `subjective`, `mixed` และค่า `NULL` ในจำนวนข้อหรือคำแนะนำ
- ไม่พบผลลัพธ์ได้โดยเลือกชุดตัวกรองที่ไม่มีในข้อมูล เช่น ปี 2500

### Demo

- แนวข้อสอบ CS261 สองรายการ พร้อมหัวข้อ จำนวนข้อ และคำแนะนำที่อ่านเข้าใจง่าย
- ระบุในชื่อและคำแนะนำว่าข้อมูลเป็นตัวอย่าง ไม่ใช่แนวข้อสอบจริง

ข้อมูลผู้เผยแพร่ไม่มีรหัสผ่าน สคริปต์จะไม่สร้างหรือแก้ข้อมูลรายวิชา และจะหยุดพร้อมแจ้งรหัสวิชาที่ขาด หากฐานข้อมูลยังไม่มีรายวิชาที่ชุดข้อมูลต้องใช้ โดยอ่านผู้สอนที่กำหนดไว้จาก Course เดิม

## วิธีรัน

รันจากโฟลเดอร์ `backend` หลังสร้างตารางตาม Task40 และเตรียมรายวิชา CS261 กับ CS102 แล้ว ตั้งค่า `DB_CONNECTION_STRING` ให้ชี้ไปยังฐานข้อมูลที่ต้องการใช้:

```powershell
python -m scripts.seed_guides --dataset test --action seed
python -m scripts.seed_guides --dataset test --action check
python -m scripts.seed_guides --dataset test --action restore
```

เปลี่ยน `test` เป็น `demo` เพื่อจัดการชุด Demo คำสั่ง `seed` รันซ้ำได้ โดยอัปเดตรายการที่มีชื่อ Seed ตรงกันแทนการเพิ่มซ้ำ `restore` ลบเฉพาะแนวข้อสอบที่มีชื่อและผู้เผยแพร่ตรงกับ dataset และลบผู้เผยแพร่ของ Seed เมื่อไม่มีแนวข้อสอบอื่นอ้างถึง

ผล `seed/check (verified)` คือจำนวนรายการ Seed ที่ตรวจตรงกับไฟล์ ส่วน `restore (removed)` คือจำนวนที่ลบจริง การเรียก restore ซ้ำจะคืนจำนวนลบเป็นศูนย์

ใช้ username `t41_test_publisher` และ `t41_demo_publisher` สำหรับชุดข้อมูลนี้เท่านั้น ทุกคำสั่งจะหยุดหากพบบัญชีชื่อนี้แต่ชื่อแสดงไม่ตรงกับ dataset

ชื่อแนวข้อสอบและรหัสวิชาใช้ค้นหารายการ Seed อย่าเปลี่ยนชื่อหรือรหัสวิชาใน dataset/ฐานข้อมูลก่อน restore เพราะสคริปต์จะค้นรายการเดิมไม่พบ การรันซ้ำรองรับการรันทีละครั้ง ไม่รองรับผู้รันสองคนพร้อมกัน เนื่องจากตาราง guides ไม่มี unique constraint สำหรับตัวระบุ Seed

จำนวนที่ check คืนเป็นจำนวนเฉพาะชุด Seed ไม่ใช่จำนวนแนวข้อสอบทั้งหมดของวิชา หากทดสอบผลกรองโดยต้องการจำนวนแน่นอน ให้ใช้ฐานข้อมูลทดสอบที่แยกจากฐานข้อมูล Demo และข้อมูลจริง

อย่าบันทึก connection string หรือรหัสผ่านลงในไฟล์ Seed หรือเอกสารนี้ ตรวจไฟล์ `.env` ก่อนรัน และเลือกฐานข้อมูลที่ใช้ทดสอบให้ถูกต้อง

## ผลตรวจ

ตรวจ `GuideSeedService` ด้วย SQLite ชั่วคราว โดยสร้างตารางจากโมเดลปัจจุบัน แล้วรัน seed, check, seed ซ้ำ และ restore แยกสำหรับแต่ละ dataset:

| ชุด | หลัง seed/check | หลัง seed ซ้ำ | หลัง restore |
|---|---:|---:|---:|
| Test | CS261: 3, CS102: 1 | จำนวนเดิม ไม่มีรายการซ้ำ | CS261: 0, CS102: 0 |
| Demo | CS261: 2 | จำนวนเดิม ไม่มีรายการซ้ำ | CS261: 0 |

ผล: ตรวจข้อมูลแต่ละแถวกับ JSON รวมถึงชื่อไทย ข้อความหลายบรรทัด และค่า `NULL` ผ่านทั้ง SQLite และ SQL Server โดยมีการเปิด Session ใหม่เพื่ออ่านข้อมูลที่บันทึกแล้วด้วย

หลังตรวจโครงสร้าง เพิ่ม regression tests และรันผ่านทั้ง 6 กรณีบน SQLite และ SQL Server:

1. seed/check/seed ซ้ำ/restore/restore ซ้ำ ใน Session และ transaction เดียว
2. restore ชุด Test แล้วชุด Demo และแนวข้อสอบของผู้เผยแพร่รายอื่นยังอยู่
3. seed และ restore ปฏิเสธ username ที่ชนกับบัญชีอื่น โดยไม่แก้หรือลบบัญชีนั้น
4. verify ไม่ผ่านแล้ว transaction ย้อนคืนข้อมูล Seed ทั้งหมด
5. ขาดรายวิชาที่จำเป็นแล้วไม่มีข้อมูล Seed ค้างบางส่วน
6. บันทึกชุด Test และ Demo แล้วเปิด Session ใหม่อ่านค่าจากฐานข้อมูลได้ตรงกับ JSON

รันจาก `backend`:

```powershell
python -m unittest discover -s test -p test_guide_seed_service.py -v
```

ตรวจบน SQL Server ด้วย connection ที่ตั้งไว้ใน `backend/.env`:

```powershell
$env:TASK41_TEST_SQLSERVER = "1"
python -m unittest discover -s test -p test_guide_seed_service.py -v
Remove-Item Env:TASK41_TEST_SQLSERVER
```

แต่ละกรณี SQL Server สร้าง schema ชื่อ `task41_test_<uuid>` และตารางภายใน outer transaction ส่วน Session ใช้ savepoint เพื่อให้กรณี rollback ไม่ลบ fixture ที่เตรียมไว้ เมื่อจบแต่ละกรณีจะ rollback outer transaction และตรวจ `sys.schemas` ว่า schema ชั่วคราวไม่เหลืออยู่ การทดสอบนี้ไม่เขียนข้อมูลลงตารางแอปพลิเคชันเดิม และยังไม่ใช่การทดสอบผ่านหน้าเว็บ

## แนวทางที่ใช้

การแยกสคริปต์จัดการข้อมูลออกจาก migration เป็นทางเลือกที่อธิบายใน [Alembic Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html#data-migrations-general-techniques) ส่วนการให้ CLI คุม Session/transaction ใช้รูปแบบ [SQLAlchemy Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it) ตำแหน่ง `backend/scripts/` เป็นการจัดโฟลเดอร์ของโปรเจกต์นี้ ไม่ใช่ชื่อที่ SQLAlchemy บังคับ

## ขอบเขต

ปัจจุบันหน้าอ่านตัวอย่างใน Frontend ใช้ข้อมูลใน `localStorage` และยังไม่ได้เรียก API/ฐานข้อมูล ชุด Seed นี้เตรียมข้อมูลในฐานข้อมูลตามโมเดลและ DAO ของ Task40 เพื่อรองรับการทดสอบฝั่งฐานข้อมูลและการเชื่อม API ในขั้นถัดไป โดยไม่แก้หน้าเว็บใน Task41
