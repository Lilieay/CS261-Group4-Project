# Task80: Docker runbook สำหรับหน้าแนวข้อสอบของฉัน

## สภาพแวดล้อมทดสอบ

ใช้ Compose project และ volume ที่แยกจากฐานข้อมูลหลัก:

- Project: cs261-task60-test
- Compose override: %TEMP%\cs261-task60-compose.override.yaml
- Volume: cs261-task60-test_sqlserver_data
- Database: CS261Group4Dev
- Frontend: http://127.0.0.1:25001
- Backend: http://127.0.0.1:28001
- SQL Server: 127.0.0.1:21434

ดูขั้นตอนเตรียม .env, override และเริ่ม SQL Server ได้ที่ [Task60 Docker runbook](../U4/U4_Task60_Docker_Runbook.md) ใช้ project และ volume ข้างต้น ห้ามใช้ down -v, ลบ volume หรือ cleanup แถวที่ผู้ใช้สร้างไว้

## Build และเริ่ม frontend หลังแก้โค้ด

จาก root repository:

    $overridePath = Join-Path $env:TEMP 'cs261-task60-compose.override.yaml'
    docker compose -p cs261-task60-test -f compose.yaml -f $overridePath up -d --build frontend
    docker compose -p cs261-task60-test -f compose.yaml -f $overridePath ps

เปิด Login แล้วทดสอบ Login → รายวิชาที่แบ่งปัน → กรอง/ค้นหา → เปิดอ่าน → กลับหน้าเดิม → reload ตรวจว่า API โหลดรายการเดิมได้ และเทียบ ID/วิชากับ SQL Server โดยใช้ SELECT read-only เท่านั้น ห้ามใส่ password, token หรือ connection string ในรายงาน

## Tests

    cd frontend
    npm.cmd test
    cd ..\backend
    .\.venv\Scripts\python.exe -m pytest -q test/test_my_guides_api.py

DAO SQL Server suite ใช้ transaction และ schema ชั่วคราวตาม backend/test/test_my_guide_dao.py; ทำตามคำสั่งใน Task60 runbook ผ่าน backend container และตรวจผลว่า schema rollback แล้ว อย่ารายงาน SQLite เป็น SQL Server

รัน DAO suite จาก root repository:

    $testPath = Join-Path (Get-Location) 'backend\test'
    docker compose -p cs261-task60-test -f compose.yaml -f $overridePath run --rm --no-deps -e TASK68_TEST_SQLSERVER=1 -v "${testPath}:/app/test:ro" backend python -m unittest discover -s test -p test_my_guide_dao.py -v

## หยุดบริการ

    docker compose -p cs261-task60-test -f compose.yaml -f $overridePath down

คำสั่งนี้หยุด containers แต่เก็บ volume ทดสอบและรายการที่สร้างไว้
