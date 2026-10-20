# Task26: ข้อมูลรายวิชาเริ่มต้นและวิธีจัดการ Seed

ข้อมูลรายวิชาอ้างอิงจากระบบค้นหารายวิชาของสำนักทะเบียน มหาวิทยาลัยธรรมศาสตร์ที่ [vnweb68.reg.tu.ac.th/registrar/classinfo](https://vnweb68.reg.tu.ac.th/registrar/classinfo) ตรวจข้อมูลวันที่ 18 ตุลาคม 2026 โดยเลือกภาคเรียนที่ 1 ปีการศึกษา 2569 ศูนย์รังสิต ระดับปริญญาตรีภาคปกติ และหลักสูตร 2566 รวมกลุ่มเรียนที่มีรหัสวิชาเดียวกันเป็นหนึ่งรายการ และรวบรวมชื่อผู้สอนที่ไม่ซ้ำจากกลุ่มเรียนเหล่านั้น รายชื่อผู้สอนจึงเป็นข้อมูลตามผลค้นหาที่เลือก ไม่ใช่การกำหนดผู้สอนประจำรายวิชา

ชุดข้อมูลมี 24 รายวิชา ไม่นำ CS301, CS303, CS403 และ CS404 มารวม เพราะเป็นวิชาโครงงานหรือสหกิจศึกษา โดยสามวิชาหลังมีผู้สอนวิชาละ 19 คน และไม่นำรายวิชาที่มีผู้สอนมากกว่าสองคนมารวม ส่วน CS263 อยู่ในชุดข้อมูลเพราะปรากฏในผลค้นหาของสำนักทะเบียน แม้กลุ่มเรียนจะปิดแล้ว การมีรายวิชาในชุดข้อมูลไม่ได้หมายความว่ายังเปิดให้ลงทะเบียน

ชื่อรายวิชาและชื่อผู้สอนใช้ตัวสะกดตามที่สำนักทะเบียนแสดง [แบบตาราง Task22](task22-course-entity.md) และ Entity `Course` เดิมมีคอลัมน์ `instructor_name` เพียงคอลัมน์เดียว จึงรวมชื่อผู้สอนหนึ่งหรือสองคนด้วยเครื่องหมายจุลภาคและช่องว่างตามตัวอย่างของ Task22 แม้ Task21 จะกล่าวถึงฟิลด์ผู้สอนคนที่สอง แต่ Seed นี้ไม่เปลี่ยน schema ของ `Course` รายวิชา CS261 มีคำอธิบายจากสำนักทะเบียน ส่วนวิชาอื่นที่ไม่ได้เก็บคำอธิบายใช้ค่า null

ข้อมูลเริ่มต้นฉบับเต็มอยู่ใน [courses.json](../../backend/scripts/seed_data/datasets/courses.json) โดยจัดแต่ละรายวิชาและรายชื่อผู้สอนแยกบรรทัดเพื่อให้ตรวจสอบได้ง่าย

ชุด `test` เลือก CS100, CS101, CS102 และ CS261 ส่วนชุด `demo` ใช้ทั้ง 24 รายวิชา ชุดทดสอบจึงมีขนาดเล็กและมีรายวิชาที่ Task41 ต้องใช้ครบ

## คำสั่งใช้งาน

รันจากโฟลเดอร์ `backend` หลังติดตั้งแพ็กเกจตาม `requirements.txt` และตั้งค่า `DB_CONNECTION_STRING` กับ `DB_PASSWORD` ใน `backend/.env` หรือ environment ต้องสร้างฐานข้อมูลด้วย `db/init.sql` ก่อน แล้วสร้างตารางของระบบด้วย `python -m app.init_db` ก่อนเพิ่มข้อมูล Seed ครั้งแรก

รันทีละคำสั่ง:

```powershell
python -m scripts.seed_courses --dataset test --action seed
python -m scripts.seed_courses --dataset test --action check
python -m scripts.seed_courses --dataset test --action restore
python -m scripts.seed_courses --dataset demo --action seed
python -m scripts.seed_courses --dataset demo --action check
python -m scripts.seed_courses --dataset demo --action restore
```

สำหรับ Docker Compose ให้รันจากโฟลเดอร์รากของ repository ตั้งค่า `MSSQL_SA_PASSWORD` ใน `.env` ที่เก็บเฉพาะในเครื่อง เริ่ม SQL Server และใช้ `db/init.sql` สร้างฐานข้อมูลพัฒนาหากยังไม่มี จากนั้น build image และสร้างตารางของระบบก่อนเรียก CLI ที่อยู่ใน image:

```sh
docker compose build backend
docker compose up -d sqlserver
docker compose run --rm --no-deps backend python -m app.init_db
docker compose run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action seed
docker compose run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action check
docker compose run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action restore
```

CLI สร้างเฉพาะตารางติดตามเจ้าของข้อมูล Seed ชื่อ `course_seed_ownership` ก่อนทำ `seed` เท่านั้น ไม่สร้างหรือแก้ตารางข้อมูลหลักของระบบ คำสั่ง seed และ restore ทำงานภายใน transaction และพิมพ์รายงานหลัง commit ส่วน `check` ไม่สร้างตารางติดตามนี้ หากยังไม่มีตารางดังกล่าว check จะตรวจความตรงกันของข้อมูลได้ แต่ยืนยันไม่ได้ว่าเครื่องมือเป็นผู้สร้างข้อมูล และ restore จะเก็บแถวที่ตรงกันไว้ในฐานะข้อมูลที่เครื่องมือไม่ได้เป็นเจ้าของ

เครื่องมือติดตามเฉพาะแถวที่เครื่องมือเพิ่มเอง หากข้อมูลเดิมตรงกันจะใช้ข้อมูลเดิมโดยไม่อ้างสิทธิ์เป็นเจ้าของ ชื่อรายวิชาและชื่อผู้สอนในชุดข้อมูลต้องตรงกับแถวเดิม รวมถึงคำอธิบายหากชุดข้อมูลระบุไว้ หากคำอธิบายเป็น null เพราะไม่ได้เก็บข้อมูล จะคงค่าเดิมในฐานข้อมูลไว้

Restore ลบรายวิชาที่เครื่องมือติดตามเฉพาะเมื่อข้อมูลทุกฟิลด์ยังตรงกับข้อมูลที่บันทึกไว้ และไม่มีแนวข้อสอบอ้างถึง หากชุด test และ demo ใช้แถวร่วมกัน จะถอนเฉพาะสิทธิ์ของชุดที่ restore และเก็บสิทธิ์ของอีกชุดไว้ สำหรับแถวที่เหลือเจ้าของชุดสุดท้าย หากข้อมูลถูกแก้หรือมีรายการอ้างถึง จะเก็บทั้งแถวและสิทธิ์ไว้ พร้อมระบุเหตุผลในรายงานเพื่อให้ผู้ดูแลตรวจและลองใหม่ภายหลัง หากผิดข้อกำหนดของฐานข้อมูลจะยกเลิก transaction

รัน seed, check และ restore ทีละ process ตารางติดตามและการตรวจก่อนเริ่มรองรับการรันซ้ำตามลำดับ แต่เครื่องมือไม่ได้ประสานการรัน seed และ restore พร้อมกันหลาย process

## การตรวจสอบ

จาก `backend` รันชุดทดสอบ SQLite เฉพาะส่วนด้วย `python -m pytest test/test_course_seed_service.py`

หากทดสอบ SQL Server ผ่าน PowerShell ให้ตั้ง `$env:TASK26_TEST_SQLSERVER = '1'` ก่อนรันคำสั่งทดสอบเดิม บัญชีที่ตั้งค่าต้องมีสิทธิ์สร้าง schema ทดสอบ ชุดทดสอบสร้าง schema ชั่วคราวแยกแล้ว rollback เมื่อจบ ส่วนกรณีไม่มีตารางติดตามเจ้าของข้อมูลใช้ฐานข้อมูล SQLite แยกทั้งสองโหมด

CLI จริงเขียนข้อมูลลงฐานข้อมูลพัฒนาที่ตั้งค่าไว้ เมื่อจบการตรวจที่บันทึกในรายงาน ฐานข้อมูลมีชุด demo จำนวน 24 รายวิชา ดูรายละเอียดใน [รายงานผลตรวจจริง](Task26-verification-report.md)
