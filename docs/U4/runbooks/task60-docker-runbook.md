# Task60: คู่มือทดสอบการเผยแพร่บน Docker

คู่มือนี้ใช้ Compose project และ SQL volume แยก เพื่อไม่เขียนข้อมูลลงฐานข้อมูลหลักของเครื่อง

## 1. เตรียมค่าในเครื่อง

ที่ root repository สร้าง .env จาก .env.example หากยังไม่มี แล้วตั้ง MSSQL_SA_PASSWORD สำหรับ SQL Server เครื่องนี้ และ TU_API_MODE=mock ห้าม commit .env หรือใส่ password, TU API key หรือ token จริงในรายงาน

## 2. สร้าง Compose override ใน OS temp

เปิด PowerShell ที่ root repository แล้วสร้างไฟล์ override:

~~~powershell
$overridePath = Join-Path $env:TEMP 'cs261-task60-compose.override.yaml'
@'
services:
  sqlserver:
    ports: !override
      - "127.0.0.1:21434:1433"
  backend:
    ports: !override
      - "127.0.0.1:28001:8000"
  frontend:
    ports: !override
      - "127.0.0.1:25001:5000"
volumes:
  sqlserver_data:
    name: cs261-task60-test_sqlserver_data
'@ | Set-Content -LiteralPath $overridePath -Encoding utf8
$composeArgs = @('-p', 'cs261-task60-test', '-f', 'compose.yaml', '-f', $overridePath)
~~~

ไฟล์นี้อยู่นอก repository; project ใช้ volume cs261-task60-test_sqlserver_data และพอร์ตทดสอบเฉพาะ

## 3. เริ่ม SQL Server และเตรียมฐานทดสอบ

~~~powershell
docker compose @composeArgs up -d sqlserver
docker compose @composeArgs ps
~~~

รอให้ SQL Server healthy แล้วสร้าง database/tables และ seed ข้อมูลทดสอบ:

~~~powershell
docker compose @composeArgs exec -T sqlserver sh -c 'SQLCMDPASSWORD="$MSSQL_SA_PASSWORD" /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C -b -i /docker-entrypoint-initdb.d/init.sql'
docker compose @composeArgs run --rm --no-deps backend python -m app.init_db
docker compose @composeArgs run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action seed
docker compose @composeArgs run --rm --no-deps backend python -m scripts.seed_guides --dataset test --action seed
docker compose @composeArgs up -d --build backend frontend
~~~

สำหรับทดสอบ ใช้บัญชี mock ตาม docs/U1/U1_Task16_Backend_Docker_Runbook.md เท่านั้น

## 4. ตรวจ flow และปิดบริการ

เปิด http://127.0.0.1:25001/login.html แล้วทดสอบ Login → upload.html → Publish → Read → เปิดรายการในคลัง CS261 และ reload หน้าอ่าน ตรวจ row ด้วย query แบบ read-only หากต้องยืนยันข้อมูลใน SQL Server

ตรวจสถานะและ log ได้ด้วย:

~~~powershell
docker compose @composeArgs ps
docker compose @composeArgs logs --tail=100 backend
~~~

หยุด containers โดยเก็บ volume ไว้:

~~~powershell
docker compose @composeArgs down
~~~

ห้ามใช้ down -v หรือลบ cs261-task60-test_sqlserver_data; volume นี้เก็บหลักฐานรายการทดสอบไว้

## 5. หลักฐานที่บันทึก

- รุ่นโค้ดและผล docker compose ps
- HTTP status ของ Login, Publish, Read และ List
- ผล validation และ unauthorized request โดยไม่บันทึก token
- ผล query ที่แสดงรายการทดสอบโดยไม่เปิดเผย credential
- ภาพ UI ที่ไม่แสดงรหัสผ่านหรือ token
