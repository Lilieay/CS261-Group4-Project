# Task16: รายงานทดสอบระบบ Docker และ end-to-end

## รุ่นและสภาพแวดล้อม

- Source revision: `4e1bd37d1c9ee262f73aa54471d5e2c7a43fec37`
- ระบบที่ทดสอบ: Windows PowerShell, Docker Compose 5.5.1, SQL Server 2022, backend Python 3.14.8, frontend Node.js 24.22.0
- Backend image SHA: `sha256:8ce7b519376d05894f37f192df7c9a157742a85376df16cc4ea5819749f7f544`
- ผลทดสอบ runtime ตามแผน: เสร็จ

## กรณีทดสอบ

| กรณี | ผลที่คาดหวัง | ผลจริง |
|---|---|---|
| เริ่ม SQL Server และ backend | `scripts/start-backend.ps1` จบด้วย exit code 0 และ backend root ตอบ 200 | ผ่านในการรันครั้งแรก |
| รัน startup script ซ้ำ | SQL Server, schema และข้อมูลเดิมยังอยู่ และ backend กลับมาพร้อมใช้งาน | ผ่าน; mock user มีหนึ่งแถวและ ID `1002` คงเดิม |
| เริ่ม frontend | `docker compose up -d --build frontend` จบด้วย exit code 0 และ frontend container เริ่มทำงาน | ผ่าน |
| รัน test suite ใน backend image | ใช้ test directory ที่ mount แบบ read-only และคำสั่ง `python -m pytest -p no:cacheprovider test -q` | ผ่าน 106 tests และ 46 subtests; มี Starlette/httpx deprecation warning หนึ่งรายการ |
| Restart backend process | Token เดิมใช้ไม่ได้, status แสดง `logged_in=false`, login ใหม่ได้ database user ID เดิม | ผ่านผ่าน frontend proxy; ID `1002` คงเดิม |
| Storage failure | Login ตอบ 503 โดยไม่ออก token | ผ่านใน isolated TestClient probe ที่ ODBC connect ไป `127.0.0.1:1` ล้มเหลว; production SQL Server ยังทำงาน |
| Backend down ใน browser | หน้า login แสดงข้อความผิดพลาดและเปิดให้ retry หลัง backend กลับมา | ผ่าน; หยุด backend, ส่ง login, เริ่ม backend ใหม่ รอ root readiness แล้ว retry สำเร็จ |
| OpenAPI route inventory | จำนวน paths และ guide methods คงเดิมก่อนและหลังการทดสอบ | ผ่าน; 11 paths เหมือนเดิม |
| Container state หลังตรวจ | SQL Server, backend และ frontend ยังทำงาน | ทั้งสาม containers ยังทำงาน; SQL Server health เป็น healthy |

## บันทึกผล

การตรวจใช้ TU mock และไม่ครอบคลุมการยืนยันตัวตนกับ TU จริง Redirect ไป `courses.html` ยืนยันเฉพาะผล login flow; หน้า courses ยังแสดงข้อมูล preview และการตรวจนี้ไม่ได้ยืนยัน session integration หรือ access guard ของหน้านั้น ห้ามลบฐานข้อมูลหรือ volume เดิม

คำสั่งทดสอบใน backend image ใช้ host path แบบ absolute สำหรับ `backend/test` และ mount แบบ read-only:

```powershell
$testPath = (Resolve-Path 'backend/test').Path
docker compose run --rm --no-deps --volume "${testPath}:/app/test:ro" backend python -m pytest -p no:cacheprovider test -q
```
