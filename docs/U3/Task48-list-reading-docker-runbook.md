# คู่มือเริ่มระบบและตรวจ Task48 บน Docker

คู่มือนี้สร้าง environment ทดสอบแยกสำหรับหน้าแนวข้อสอบ ใช้ Compose project และ volume ชื่อใหม่ ไม่หยุดหรือลบ SQL Server volume ของ environment หลัก

## ตรวจเงื่อนไขก่อนเริ่ม

1. เปิด Docker Desktop และตรวจว่า `docker info` ทำงาน
2. เปิด PowerShell ที่ root ของ repository
3. ตรวจว่ามี `.env` ที่กำหนด `MSSQL_SA_PASSWORD` โดยใช้รหัสผ่านของ test environment เท่านั้น
4. ตรวจว่า ports 21433, 28000 และ 25000 ว่าง

## สร้าง Compose override ใน OS temp

เก็บ override ไว้นอก repository:

```powershell
$overridePath = Join-Path $env:TEMP 'cs261-task48-compose.override.yaml'
$override = @"
services:
  sqlserver:
    ports: !override
      - "127.0.0.1:21433:1433"
  backend:
    environment:
      DB_CONNECTION_STRING: "DRIVER={ODBC Driver 18 for SQL Server};SERVER=sqlserver,1433;DATABASE=CS261Group4Dev;UID=sa;Encrypt=yes;TrustServerCertificate=yes"
      TU_API_MODE: "mock"
    ports: !override
      - "127.0.0.1:28000:8000"
  frontend:
    ports: !override
      - "127.0.0.1:25000:5000"
"@
[System.IO.File]::WriteAllText($overridePath, $override, (New-Object System.Text.UTF8Encoding($false)))
$composeArgs = @('-p','cs261-task48-test','-f','compose.yaml','-f',$overridePath)
```

Compose project `cs261-task48-test` ใช้ volume `cs261-task48-test_sqlserver_data` แยกจาก project หลัก ทุกคำสั่งด้านล่างต้องใช้ `$composeArgs` ชุดเดิม

## เริ่ม SQL Server และสร้างตาราง

```powershell
docker compose @composeArgs up -d --wait --wait-timeout 120 sqlserver
if ($LASTEXITCODE -ne 0) { throw 'SQL Server did not become healthy.' }

docker compose @composeArgs exec -T sqlserver sh -c 'SQLCMDPASSWORD="$MSSQL_SA_PASSWORD" /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C -b -i /docker-entrypoint-initdb.d/init.sql'
if ($LASTEXITCODE -ne 0) { throw 'Database bootstrap failed.' }

docker compose @composeArgs build backend frontend
if ($LASTEXITCODE -ne 0) { throw 'Container image build failed.' }

docker compose @composeArgs run --rm --no-deps backend python -m app.init_db
if ($LASTEXITCODE -ne 0) { throw 'ORM table creation failed.' }
```

`db/init.sql` สร้าง database เมื่อยังไม่มี ส่วน `app.init_db` สร้างตาราง ORM ที่ขาดอยู่ คำสั่งนี้ไม่ลบ database หรือ volume

## Seed และตรวจข้อมูล

ใช้ test dataset ที่เหมาะกับการทดสอบ filter และรายละเอียด:

```powershell
docker compose @composeArgs run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action seed
if ($LASTEXITCODE -ne 0) { throw 'Course seed failed.' }
docker compose @composeArgs run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action check
if ($LASTEXITCODE -ne 0) { throw 'Course seed check failed.' }
docker compose @composeArgs run --rm --no-deps backend python -m scripts.seed_guides --dataset test --action seed
if ($LASTEXITCODE -ne 0) { throw 'Guide seed failed.' }
docker compose @composeArgs run --rm --no-deps backend python -m scripts.seed_guides --dataset test --action check
if ($LASTEXITCODE -ne 0) { throw 'Guide seed check failed.' }
```

สคริปต์ seed รองรับ `seed`, `check` และ `restore` ให้ตรวจ dataset ก่อน restore ทุกครั้ง ชุดนี้เขียนเฉพาะ database ใน Compose project ทดสอบ ห้ามสลับ `$composeArgs` ไปยัง project หลัก

## เริ่มและตรวจบริการ

```powershell
docker compose @composeArgs up -d --wait --wait-timeout 120 backend frontend
if ($LASTEXITCODE -ne 0) { throw 'Application services did not become healthy.' }
docker compose @composeArgs ps
```

เปิด `http://127.0.0.1:25000/login.html` และใช้บัญชี mock ที่ระบุใน [คู่มือ Docker Task16](../U1/U1_Task16_Backend_Docker_Runbook.md)

ตรวจหน้า API ได้ที่ `http://127.0.0.1:28000/docs` และ health check ที่ `http://127.0.0.1:28000/`

## ตรวจเส้นทางรายการและหน้าอ่าน

1. Login ใน test environment แล้วค้นหารายวิชา `CS261`
2. เปิดคลังและตรวจว่ามีรายการ seed 3 รายการ
3. เลือกปี `2568` แล้วตรวจว่ามี 2 รายการ
4. เลือกภาคเรียน `2` เพิ่ม แล้วตรวจ empty state
5. ล้างตัวกรอง แล้วตรวจว่ารายการกลับมา 3 รายการ
6. เปิดรายการแรก ตรวจผู้สอน ผู้เผยแพร่ หัวข้อ รูปแบบ จำนวนข้อ และคำแนะนำ
7. Reload หน้าอ่าน แล้วตรวจว่ารายละเอียดเดิมยังแสดง
8. กลับหน้ารายการ แล้วตรวจว่าตัวกรองเดิมยังอยู่
9. เปิด `read-courses.html?source=api&courseId=4&course=CS261&guide=999` แล้วตรวจว่าไม่พบแนวข้อสอบ

จด browser, SHA, seed dataset, ผลจริง และหลักฐาน โดยไม่บันทึก token หรือข้อมูลส่วนบุคคล

## เก็บ environment ไว้สำหรับตรวจซ้ำ

Compose project และ volume ทดสอบนี้เก็บไว้สำหรับทำซ้ำ ห้ามใช้ `docker compose down -v` และห้ามสั่งลบ volume `cs261-group4_sqlserver_data` การปิด container ทดสอบชั่วคราวให้ใช้คำสั่งนี้โดยตรวจ project name ก่อน:

```powershell
docker compose @composeArgs stop
```

เริ่มต่อได้ด้วย `docker compose @composeArgs start` ตรวจสถานะด้วย `docker compose @composeArgs ps`