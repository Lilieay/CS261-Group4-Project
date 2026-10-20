# CS261 Group 4

เว็บคลังรายวิชาและแนวข้อสอบ ใช้ Frontend (Node.js/Express), Backend (FastAPI) และ SQL Server 2022 บน Docker

## เปิดชุดทดสอบ Task60 ที่เตรียมไว้ในเครื่องนี้

หาก containers ของ Task60 ยังทำงานอยู่ เปิด [หน้า Login ชุดทดสอบ](http://127.0.0.1:25001/login.html) ได้ทันที โดยใช้บัญชี mock ด้านล่าง

ชุดนี้ใช้ Compose project `cs261-task60-test` และ volume `cs261-task60-test_sqlserver_data` แยกจากฐานข้อมูลหลัก พอร์ต Frontend คือ `25001`, Backend คือ `28001` และ SQL Server คือ `21434`

ดูวิธีเริ่มชุดนี้ใหม่ใน [Docker runbook ของ Task60](docs/U4/U4_Task60_Docker_Runbook.md) คำสั่งในหัวข้อถัดไปใช้ชุดปกติซึ่งเปิด Frontend ที่พอร์ต `5000`

## รันเว็บด้วย Docker ตั้งแต่เริ่มต้น

### 1. เตรียมเครื่องและไฟล์ตั้งค่า

เปิด Docker Desktop ให้ engine ทำงาน แล้วเปิด PowerShell ที่โฟลเดอร์รากของ repository ซึ่งมี `compose.yaml`

สร้าง `.env` จากตัวอย่างเฉพาะเมื่อยังไม่มีไฟล์:

~~~powershell
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
}
~~~

เปิดไฟล์ `.env` แล้วกำหนดค่า:

~~~dotenv
MSSQL_SA_PASSWORD=<รหัสผ่าน SQL Server ของเครื่องนี้>
TU_API_MODE=mock
~~~

รหัสผ่าน SQL Server ใหม่ต้องมีอย่างน้อย 8 ตัวอักษรและผ่านข้อกำหนดความซับซ้อนของ SQL Server เช่น ใช้ตัวพิมพ์ใหญ่ ตัวพิมพ์เล็ก ตัวเลข และสัญลักษณ์ร่วมกัน หากใช้ volume เดิม ให้ใช้รหัสผ่านเดิมที่สร้าง SQL Server นั้น เก็บ `.env` ไว้ในเครื่องและอย่า commit

โหมด `mock` ใช้บัญชีทดสอบในเครื่อง จึงไม่ต้องตั้ง TU API key

### 2. เริ่ม SQL Server และ Backend

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1
~~~

สคริปต์ build Backend, รอ SQL Server healthy, รัน `db/init.sql` เพื่อสร้าง database, สร้างตาราง ORM ที่ยังไม่มี และเปิด Backend เมื่อสำเร็จจะแสดง URL ของ Backend และ API docs

### 3. Seed รายวิชาและแนวข้อสอบตัวอย่าง

~~~powershell
docker compose exec backend python -m scripts.seed_courses --dataset demo --action seed
docker compose exec backend python -m scripts.seed_guides --dataset test --action seed
~~~

ชุด demo มีรายวิชา 24 วิชาจากไฟล์ courses.json ส่วนแนวข้อสอบใช้ชุด test ซึ่งมี CS261 จำนวน 3 รายการ และ CS102 จำนวน 1 รายการ รายการที่เผยแพร่เพิ่มจะเก็บอยู่ในฐานข้อมูลด้วย

ตรวจชุด seed ได้ด้วย:

~~~powershell
docker compose exec backend python -m scripts.seed_courses --dataset demo --action check
docker compose exec backend python -m scripts.seed_guides --dataset test --action check
~~~

### 4. เปิด Frontend

~~~powershell
docker compose up -d --build frontend
docker compose ps
~~~

| บริการ | URL |
|---|---|
| หน้า Login | http://127.0.0.1:5000/login.html |
| ค้นหารายวิชา | http://127.0.0.1:5000/courses.html |
| เผยแพร่แนวข้อสอบ | http://127.0.0.1:5000/upload.html |
| Backend health | http://127.0.0.1:8000/ |
| API docs | http://127.0.0.1:8000/docs |

เปิดหน้าเว็บผ่าน Frontend server ตาม URL นี้ เพื่อให้การ Login และเรียก API ผ่าน proxy ทำงานครบ

## บัญชี mock สำหรับทดสอบ

| รหัสนักศึกษา | รหัสผ่าน | ชื่อที่แสดง |
|---|---|---|
| `6800000000` | `0000000000000` (เลขศูนย์ 13 ตัว) | Student User |

บัญชีนี้ใช้เมื่อ `TU_API_MODE=mock` เท่านั้น ใช้ทดสอบระบบโดยไม่ยืนยันบัญชีมหาวิทยาลัยจริง

## ลองใช้งานหน้าเว็บ

### อัปเดต branch `fix/read-courses`

Branch นี้เพิ่มตาราง `saved_guides` สำหรับบันทึกแนวข้อสอบแยกตามบัญชีผู้ใช้
ก่อนทดลองปุ่มบันทึก ให้สร้างตารางที่เพิ่มมาและเริ่มบริการใหม่:

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1
docker compose up -d --build frontend
~~~

สคริปต์สร้างเฉพาะตารางที่ยังไม่มี ไม่ลบข้อมูลเดิม หากรัน Backend ด้วย Python ในเครื่อง
ให้ใช้คำสั่งต่อไปนี้จากโฟลเดอร์ `backend` แล้วเริ่ม Backend ใหม่:

~~~powershell
.\.venv\Scripts\python.exe -m app.init_db
~~~

การบันทึกใช้ข้อมูลแนวข้อสอบจริงจาก API ไม่ใช้รายการตัวอย่างที่เคยเก็บใน browser
ลองเปิดอ่านแนวข้อสอบ กด **บันทึก** แล้วเปิด **รายวิชาที่บันทึก**:
รายการต้องยังอยู่หลัง reload และกด **นำออก** ได้โดยไม่ลบแนวข้อสอบต้นฉบับ
เมื่อผู้เผยแพร่แก้ไขหรือลบแนวข้อสอบ รายการที่บันทึกจะใช้ข้อมูลล่าสุด
ปุ่มออกจากระบบใน navbar จะยกเลิก token ที่ Backend และกลับหน้า Login
Session มีอายุเริ่มต้น 8 ชั่วโมง ปรับได้ด้วย `AUTH_SESSION_TTL_SECONDS` (หน่วยวินาที)
และต้องเข้าสู่ระบบใหม่เมื่อ Backend เริ่มใหม่
ระบบรีวิวคะแนนยังอยู่ใน Sprint 2

### ขั้นตอนทดสอบการเผยแพร่

1. เปิดหน้า Login แล้วเข้าสู่ระบบด้วยบัญชี mock
2. ค้นหา CS261 และเปิดคลังรายวิชา
3. ลองกรองปีการศึกษา ภาคเรียน และช่วงสอบ แล้วเปิดอ่านแนวข้อสอบ
4. เปิดเมนูอัปโหลดเอกสาร เลือกรายวิชา และกรอกข้อมูลที่มีเครื่องหมาย *
5. กดเผยแพร่ ระบบจะบันทึกลง SQL Server และเปิดหน้าอ่านของรายการที่สร้าง
6. กลับไปคลังรายวิชาเพื่อตรวจรายการใหม่ แล้ว reload หน้าอ่านเพื่อดูว่าข้อมูลยังอยู่
7. ลองส่งฟอร์มที่กรอกไม่ครบเพื่อตรวจข้อความ validation

Login, ค้นหารายวิชา, รายการแนวข้อสอบ, หน้าอ่าน, การเผยแพร่, หน้า "แนวข้อสอบของฉัน" และการแก้ไข/ย้ายรายวิชาเชื่อม API จริงแล้ว ส่วนการลบรายการยังเป็นงาน Task82

ผู้ใช้ที่ Login สำเร็จถูกเก็บใน SQL Server ส่วน token เก็บในหน่วยความจำของ Backend เมื่อ restart Backend ต้อง Login ใหม่

## ดูสถานะและหยุดระบบปกติ

~~~powershell
docker compose ps
docker compose logs --tail=100 backend frontend
docker compose down
~~~

`docker compose down` เก็บ volume และข้อมูลไว้ เมื่อต้องการเปิดใหม่ให้รันขั้นตอนเริ่ม Backend และ Frontend ด้านบน โดยใช้ `.env` เดิม อย่าใช้ `down -v` เพราะจะลบ volume ฐานข้อมูล

หากพอร์ต `1433`, `8000` หรือ `5000` ถูกใช้งานอยู่ ให้ใช้ [ชุดทดสอบแยกของ Task60](docs/U4/U4_Task60_Docker_Runbook.md) ที่พอร์ต `21434`, `28001` และ `25001`

## เอกสารเพิ่มเติม

- [คู่มือ Backend และ Login](docs/U1/U1_Task16_Backend_Docker_Runbook.md)
- [คู่มือทดสอบ Task60 ด้วย project และ volume แยก](docs/U4/U4_Task60_Docker_Runbook.md)
- [ผลทดสอบ UI–API ของ Task60](docs/U4/U4_Task60_UI_API_Test_Report.md)
- [ผลทดสอบ API–DAO ของ Task60](docs/U4/U4_Task60_API_DAO_Test_Report.md)
- [ผล System Test ของ Task60](docs/U4/U4_Task60_System_Test_Report.md)

- [Task82 deletion flow and verification](docs/U5/U5_Task82_Delete_My_Guides_Test_Report.md)
