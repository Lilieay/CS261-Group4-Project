# Task60: คู่มือเริ่มระบบ สร้างตาราง และ Seed

## 1. เตรียมค่าในเครื่อง

ที่ root repository สร้าง `.env` จาก `.env.example` และกำหนดเฉพาะค่าที่เครื่องต้องใช้:

```text
MSSQL_SA_PASSWORD=<รหัสผ่าน SQL Server ชั่วคราวของเครื่อง>
TU_API_MODE=mock
```

ห้าม commit `.env` และห้ามใส่ password, TU API key หรือ token จริงในรายงาน

## 2. เริ่ม SQL Server และ Backend

เปิด Docker Desktop แล้วรันจาก root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1
```

สคริปต์จะ build image, เปิด SQL Server, รอ health check, รัน `app.init_db`, เปิด Backend และตรวจ `http://127.0.0.1:8000/`

ถ้าต้องการเปิด Frontend ด้วย:

```powershell
docker compose up -d frontend
```

เปิด `http://127.0.0.1:5000`

## 3. สร้างตารางและ Seed

ถ้าไม่ได้ใช้สคริปต์เริ่มระบบ ให้รันจาก root ตามลำดับ:

```powershell
docker compose up -d sqlserver
docker compose run --rm --no-deps backend python -m app.init_db
docker compose run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action seed
docker compose run --rm --no-deps backend python -m scripts.seed_guides --dataset test --action seed
docker compose up -d backend frontend
```

สำหรับข้อมูลสาธิต ใช้ `--dataset demo` แทน `test` และตรวจข้อมูลก่อนใช้งาน:

```powershell
docker compose run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action check
docker compose run --rm --no-deps backend python -m scripts.seed_guides --dataset test --action check
```

## 4. ตรวจสถานะและหยุดระบบ

```powershell
docker compose ps
docker compose logs --tail=100 backend
docker compose down
```

`docker compose down` ไม่ลบ volume SQL Server ข้อมูลจึงยังอยู่ หากต้องการลบข้อมูลทดสอบต้องตรวจเป้าหมายให้แน่ใจก่อน

## 5. หลักฐานที่ต้องแนบ

- commit ที่ทดสอบ
- `docker compose ps` ที่เห็น services พร้อม
- ผล health check/หน้าเว็บที่เปิดได้
- ผล API และผลในฐานข้อมูลที่ไม่เปิดเผยข้อมูลลับ
- ภาพ UI ก่อน/หลังเผยแพร่ที่ปิด password/token แล้ว
- ผลจริง Pass/Fail และการตรวจรับของ PO
