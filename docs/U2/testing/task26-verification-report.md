# Task26: รายงานผลตรวจข้อมูลรายวิชาและระบบ Seed

วันที่ตรวจ: 18 ตุลาคม 2026 สาขา `feat/task26-course-seed` สร้างจาก `integration/sprint1` ที่ commit `228a6f8` โดยตรง

รุ่นโค้ดที่ตรวจ: `ebf07d1` โดยข้อมูลอยู่ที่ `924ce8b`, บริการ Seed ที่ `9d7f139`, การจัดแพ็กเกจ Docker ที่ `ecccaa5` และชุดทดสอบที่ `ebf07d1`

## สภาพแวดล้อมและข้อมูล

ใช้ Windows PowerShell, Python 3.14 ในเครื่อง, Docker Desktop 29.8.2 และ SQL Server 2022 Developer ผ่าน Docker Compose เก็บข้อมูลรับรองไว้ในไฟล์ environment ที่ Git ไม่ติดตาม

อ่านข้อมูลสำนักทะเบียนผ่าน Chrome ที่ผู้ใช้เปิดไว้ที่ [ระบบค้นหารายวิชา TU](https://vnweb68.reg.tu.ac.th/registrar/classinfo) ผลค้นหาสองหน้ามีข้อมูลกลุ่มเรียนและหลักสูตรรวม 67 แถว เมื่อกรองหลักสูตร 2566 และใช้เงื่อนไขคัดผู้สอนและรายวิชาตามเอกสารแล้ว เหลือรายวิชาไม่ซ้ำ 24 วิชา ไม่มีการบันทึกตัวระบุบัญชีหรือข้อมูล session

ก่อนตรวจ CLI มี courses = 0, guides = 0 และ users = 1 หลังตรวจมี courses = 24, guides = 0, users = 1 และรายการติดตามเจ้าของชุด demo = 24

## ผลตรวจจริง

| รหัส | ข้อมูลและผลที่คาดหวัง | ผลจริง | สถานะ |
|---|---|---|---|
| T26-DATA | ใช้ชื่อจากสำนักทะเบียน มีผู้สอนหนึ่งหรือสองคน และไม่รวมวิชาโครงงานหรือสหกิจ | มี 24 รายการ ไม่มี CS301, CS303, CS403, CS404 และ CS261 มีคำอธิบายภาษาไทยจริง | ผ่าน |
| T26-UNIT | ตรวจระบบ Seed รายวิชาและพฤติกรรม Seed เดิมของ Task41 บน SQLite | ผ่าน 20 tests และ 4 subtests | ผ่าน |
| T26-SQL | รันชุดทดสอบเดิมโดยใช้ schema แยกบน SQL Server | ผ่าน 20 tests และ 4 subtests ไม่เหลือ schema ชั่วคราว | ผ่าน |
| T26-CLI-01 | Seed ชุด test แล้ว check จากนั้น seed ซ้ำ | ครั้งแรกเพิ่ม 4 รายการ check ตรงกัน 4 รายการ และรันซ้ำใช้ 4 รายการเดิมโดยไม่เพิ่มแถว | ผ่าน |
| T26-CLI-02 | Restore ชุด test สองครั้ง | ครั้งแรกลบ 4 รายการ ครั้งที่สองลบ 0 รายการ | ผ่าน |
| T26-CLI-03 | Seed และ check ชุด demo ด้วย process แยกกัน | เพิ่ม 24 รายการ และตรวจตรงกันครบทั้ง 24 รายการ | ผ่าน |
| T26-DAO | เปิด process ใหม่แล้วเรียก `CourseDAO.search('cs261')` และ `get_by_id` | คืน CS261 เพียงหนึ่งรายการ ชื่อผู้สอนและคำอธิบายภาษาไทยตรงกับชุดข้อมูล | ผ่าน |
| T26-SAFE | รักษาข้อมูลที่ไม่เกี่ยวข้องและขอบเขต transaction ของผู้เรียก | จำนวนผู้ใช้เดิมคงที่ 1 ราย ผ่านกรณีข้อมูลถูกแก้ ไม่มีเจ้าของ มีรายการอ้างถึง ใช้ร่วมกัน และผู้เรียก rollback | ผ่าน |
| T26-IMPORT | ตั้งค่า ORM mapper ใน Python interpreter ใหม่ | Regression test และ process จริงใน Docker ผ่านหลังลงทะเบียนโมเดล User ที่ relationship อ้างถึง | ผ่าน |

## วิธีรันทดสอบซ้ำ

รัน SQLite จากโฟลเดอร์ `backend`:

```powershell
python -m pytest -p no:cacheprovider test/test_course_seed_service.py test/test_guide_seed_service.py -q
```

รัน SQL Server จากโฟลเดอร์รากของ repository:

```powershell
$task26Tests = (Resolve-Path backend/test).Path
docker compose run --rm --no-deps -e TASK26_TEST_SQLSERVER=1 -e TASK41_TEST_SQLSERVER=1 -v "${task26Tests}:/task26-tests:ro" backend python -m pytest -p no:cacheprovider /task26-tests/test_course_seed_service.py /task26-tests/test_guide_seed_service.py -q
```

แต่ละชุดทดสอบสร้าง schema ชั่วคราวของตนเองบน SQL Server แล้ว rollback เมื่อจบ ไม่ใช่ทุกกรณีที่เข้าถึง SQL Server โดยกรณีแปลงข้อมูลและ import บางกรณีไม่ใช้ฐานข้อมูล และกรณีไม่มีตารางติดตามเจ้าของข้อมูลสร้าง SQLite โดยตรง ส่วน T26-CLI-01 ถึง T26-CLI-03 ใช้ CLI จริงตรวจแยกว่าข้อมูลถูกบันทึกถาวรในฐานข้อมูลพัฒนา

การรัน CLI จริงครั้งแรกพบว่ายังไม่ได้ลงทะเบียน mapper ของ `User` ซึ่งชุดทดสอบภายใน process เดียวไม่พบเพราะ import User เอง ได้เพิ่ม regression test ที่เปิด Python interpreter ใหม่เพื่อตรวจกรณีนี้ โดยกำหนดโฟลเดอร์ทำงานจากโมดูลบริการที่ติดตั้งไว้ ทำให้รันทดสอบได้แม้ mount ชุดทดสอบเข้า Docker แยกต่างหาก

## ขอบเขตและข้อจำกัดของผลตรวจ

Task26 เพิ่มข้อมูลลงฐานข้อมูลเท่านั้น ไม่ต้องใช้ Task28 หรือสาขา Task16 ที่ยังไม่ merge ในขณะตรวจ หน้าเว็บ preview ณ รุ่นที่ตรวจยังไม่ได้เชื่อมข้อมูลเหล่านี้ ผลตรวจจึงไม่ครอบคลุม Course API การเชื่อมหน้าเว็บ หรือการซิงก์สำนักทะเบียน รายชื่อผู้สอนเป็นข้อมูล ณ ภาคเรียนที่เลือก และไม่ได้เก็บคำอธิบายของรายวิชาอื่นนอกจาก CS261

Seed และ restore รองรับการทำงานทีละ process เครื่องมือตรวจรายการอ้างอิงจาก Guide และอาศัยข้อกำหนดของฐานข้อมูลให้ rollback เมื่อมี foreign key อื่นที่ห้ามลบ เพิ่มเฉพาะตารางติดตามเจ้าของข้อมูล Seed โดยไม่เปลี่ยนนิยามตารางข้อมูลหลักของระบบ
