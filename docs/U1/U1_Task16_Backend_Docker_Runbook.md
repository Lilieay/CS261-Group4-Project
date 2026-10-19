# Task16: คู่มือเริ่ม Backend และ Docker

## เตรียมค่าและเริ่มบริการ

1. เปิด PowerShell ที่โฟลเดอร์รากของ repository
2. หากยังไม่มี `.env` ให้คัดลอก `.env.example` เป็น `.env` หากมีแล้วให้ใช้ไฟล์เดิม
3. กำหนด `MSSQL_SA_PASSWORD` ใน `.env` หากใช้ volume เดิมให้ใช้รหัสเดิมที่สร้าง SQL Server นั้น และเก็บไฟล์นี้ไว้ในเครื่อง
4. ตั้ง `TU_API_MODE=mock` สำหรับการพัฒนาและตรวจระบบในเครื่อง
5. เริ่ม SQL Server และ backend ด้วยคำสั่งนี้

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1
   ```

สคริปต์สร้าง backend image รอให้ SQL Server health check ผ่าน เรียก `db/init.sql` สร้างตาราง ORM ที่ยังไม่มี แล้วตรวจ `http://127.0.0.1:8000/` สคริปต์ไม่ลบ volume หรือข้อมูลเดิม การรันซ้ำจึงใช้ฐานข้อมูลเดิม

เริ่ม frontend แยกหลัง backend พร้อมแล้ว

```powershell
docker compose up -d --build frontend
```

เปิดหน้า Login ที่ <http://127.0.0.1:5000/login.html> และเอกสาร API ที่ <http://127.0.0.1:8000/docs>

## บัญชี mock และการเข้าสู่ระบบ

เมื่อ `TU_API_MODE=mock` ใช้บัญชีสำหรับทดสอบนี้ได้

| Username | Password | Role |
|---|---|---|
| `6800000000` | `0000000000000` | student |

บัญชี mock ใช้ทดสอบการไหลของระบบเท่านั้น ไม่ยืนยันบัญชีมหาวิทยาลัยจริง หากตั้ง `TU_API_MODE=real` ระบบต้องได้รับ URL และ application key ที่ได้รับอนุญาต การตรวจอัตโนมัติไม่เรียก TU จริง

เปิด `/docs` แล้วเรียก `POST /api/auth/login` จากนั้นกด Authorize และวางค่า `access_token` เพื่อเรียก `GET /api/auth/status`, `GET /api/auth/me` และ `POST /api/auth/logout` หน้าเว็บส่งคำขอผ่าน proxy ที่ `/api/auth` และเก็บ token ใน `sessionStorage`

การ redirect ไป `courses.html` ยืนยันเฉพาะผล login flow หน้านี้ยังแสดงข้อมูล preview จึงไม่ยืนยันการเชื่อม profile หรือการควบคุมสิทธิ์ด้วย session

ฐานข้อมูลเก็บ user ที่ผ่านการตรวจสอบก่อนออก token `AuthService` เก็บ token ในหน่วยความจำของ backend เมื่อ backend restart token เดิมใช้ไม่ได้ ผู้ใช้ล็อกอินใหม่ได้ด้วย user ID เดิมจากฐานข้อมูล Token ไม่มีการกำหนดอายุหรือการเก็บข้ามการ restart ใน Task16

## Seed ข้อมูลตัวอย่าง (ไม่จำเป็นสำหรับ login)

การ seed เพิ่มข้อมูลรายวิชาและแนวข้อสอบสำหรับลอง API หน้าเว็บส่วนที่ยังเป็น preview ไม่ได้อ่านข้อมูลเหล่านี้ บัญชี mock สำหรับ login ไม่ต้อง seed

```powershell
docker compose exec backend python -m scripts.seed_courses --dataset demo --action seed
docker compose exec backend python -m scripts.seed_guides --dataset demo --action seed
```

ตรวจชุดข้อมูลด้วย `--action check` และนำเฉพาะข้อมูลที่ seed โดยเครื่องมือนี้ออกด้วย `--action restore` ใช้ `--dataset test` แทน `demo` เมื่อต้องการชุดข้อมูลทดสอบ

## ข้อจำกัดของฐานข้อมูล

`db/init.sql` สร้าง `CS261Group4Dev` เมื่อฐานข้อมูลยังไม่มี ส่วน `python -m app.init_db` สร้างตาราง ORM ที่ขาดอยู่ แต่ไม่ทำ migration สำหรับการเปลี่ยน schema
