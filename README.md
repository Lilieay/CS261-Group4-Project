# CS261 Group 4

เว็บคลังรายวิชาและแนวข้อสอบ ใช้ Frontend (Node.js/Express), Backend (FastAPI) และ SQL Server 2022 บน Docker

คำสั่งใช้ PowerShell บน Windows รันจาก root repository ที่มี `compose.yaml` ยกเว้นขั้นตอน clone

## ติดตั้งในเครื่องใหม่

### 1. เตรียมเครื่องและดาวน์โหลดโครงการ

ติดตั้ง Git และ Docker Desktop เปิด Docker Desktop ให้ engine พร้อมใช้งานและเลือก Linux containers เมื่อรันผ่าน Docker ไม่ต้องติดตั้ง Python, Node.js หรือ SQL Server แยกในเครื่อง

ตรวจเครื่องมือ:

~~~powershell
git --version
docker --version
docker compose version
docker info
~~~

ดาวน์โหลดโครงการและเลือก branch Sprint 1:

~~~powershell
git clone https://github.com/Lilieay/cs261-group4-100001.git
cd cs261-group4-100001
git switch integration/sprint1
git pull --ff-only
~~~

### 2. สร้างไฟล์ตั้งค่า

สร้าง `.env` เฉพาะเมื่อยังไม่มี แล้วเปิดแก้ไข:

~~~powershell
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
}
notepad .env
~~~

สำหรับ Login ด้วยบัญชี TU จริง กำหนดค่าต่อไปนี้และแทนค่าตัวอย่างด้วยข้อมูลของทีม:

~~~dotenv
MSSQL_SA_PASSWORD='ใส่รหัสผ่านฐานข้อมูลของเครื่องนี้'
TU_API_MODE=real
TU_API_URL=ใส่ TU Authentication API endpoint ของทีม
TU_API_KEY=ใส่ Application Key ของทีม
TU_API_TIMEOUT=5
AUTH_SESSION_TTL_SECONDS=28800
~~~

ขอ TU API endpoint และ Application Key จากผู้ดูแลของทีมผ่านช่องทางส่วนตัว ไม่ใส่รหัสผ่านบัญชี TU ลง `.env` ผู้ใช้กรอกรหัสผ่านบัญชีที่หน้า Login เท่านั้น

รหัสผ่าน SQL Server ใหม่ต้องมีอย่างน้อย 8 ตัวอักษรและผ่านกฎความซับซ้อน เช่น มีตัวพิมพ์ใหญ่ ตัวพิมพ์เล็ก ตัวเลข และสัญลักษณ์ร่วมกัน หากใช้ volume เดิม ให้ใช้รหัสผ่านเดิมของฐานข้อมูลนั้น อย่า commit `.env`, API key หรือ token

หากต้องการทดลองโดยไม่ติดต่อ TU ให้ตั้ง `TU_API_MODE=mock` โดยไม่ต้องใส่ `TU_API_URL` และ `TU_API_KEY` ดูบัญชีทดสอบในหัวข้อเปลี่ยนโหมด Login

### 3. สร้างฐานข้อมูลและเปิด Backend

เลือกวิธีใดวิธีหนึ่งด้านล่าง ไม่ต้องรันทั้งสองวิธี

วิธีใช้สคริปต์ PowerShell:

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1
~~~

สคริปต์ build Backend รอ SQL Server healthy รัน `db/init.sql` เพื่อสร้าง database สร้างตาราง ORM ที่ยังไม่มี และเปิด Backend เมื่อสำเร็จจะแสดง URL ของ Backend และ API docs

วิธีใช้คำสั่ง Docker Compose โดยตรง:

รันทีละคำสั่งและทำขั้นถัดไปเมื่อคำสั่งก่อนหน้าสำเร็จ เริ่มจาก build Backend และรอ SQL Server healthy:

~~~powershell
docker compose build backend
docker compose up -d --wait sqlserver
~~~

สร้าง database จาก `db/init.sql` โดยใช้รหัสผ่านจาก environment ภายใน SQL Server container:

~~~powershell
docker compose exec -T sqlserver sh -c 'SQLCMDPASSWORD="$MSSQL_SA_PASSWORD" /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C -b -i /docker-entrypoint-initdb.d/init.sql'
~~~

สร้างตาราง ORM และเปิด Backend:

~~~powershell
docker compose run --rm --no-deps backend python -m app.init_db
docker compose up -d backend
docker compose ps
~~~

ตรวจว่า Backend พร้อมรับคำขอ หากยังเชื่อมต่อไม่ได้ ให้รอสักครู่แล้วตรวจอีกครั้ง:

~~~powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/' -TimeoutSec 5
~~~

เมื่อได้ HTTP 200 ให้ทำขั้นตอนเพิ่มข้อมูลตั้งต้นและเปิด Frontend ต่อ คำสั่ง `sh -c` ด้านบนทำงานภายใน Linux container ไม่ต้องมีไฟล์ `.sh` ในเครื่อง

ขั้นตอนนี้สร้างตารางที่ขาดได้ รวมถึง `saved_guides` แต่ไม่ได้ทำ migration เปลี่ยนคอลัมน์ของตารางเดิม

### 4. เพิ่มข้อมูลตั้งต้น

เพิ่มรายวิชาจากชุด demo:

~~~powershell
docker compose exec backend python -m scripts.seed_courses --dataset demo --action seed
~~~

หากต้องการแนวข้อสอบตัวอย่างสำหรับทดลองหรือ demo ให้เพิ่มชุด test:

~~~powershell
docker compose exec backend python -m scripts.seed_guides --dataset test --action seed
~~~

แนวข้อสอบชุดนี้เป็นข้อมูลทดสอบที่บันทึกในฐานข้อมูลจริง ใช้ได้ทั้งโหมด TU จริงและ mock หากต้องการเริ่มโดยไม่มีแนวข้อสอบตัวอย่าง ให้ข้ามคำสั่ง seed แนวข้อสอบ

ตรวจข้อมูลที่ seed แล้ว โดยรันเฉพาะชุดที่ได้เพิ่มไว้:

~~~powershell
docker compose exec backend python -m scripts.seed_courses --dataset demo --action check
docker compose exec backend python -m scripts.seed_guides --dataset test --action check
~~~

### 5. เปิด Frontend

~~~powershell
docker compose up -d --build frontend
docker compose ps
Start-Process 'http://127.0.0.1:5000/login.html'
~~~

ต้องเห็นบริการ `sqlserver`, `backend` และ `frontend` ทำงาน โดย `sqlserver` มีสถานะ healthy

| บริการ | ที่อยู่ |
|---|---|
| หน้า Login | http://127.0.0.1:5000/login.html |
| ค้นหารายวิชา | http://127.0.0.1:5000/courses.html |
| เผยแพร่แนวข้อสอบ | http://127.0.0.1:5000/upload.html |
| Backend health | http://127.0.0.1:8000/ |
| API docs | http://127.0.0.1:8000/docs |
| SQL Server สำหรับเครื่องมือเชื่อมฐานข้อมูล | `localhost,1433` |

เปิดเว็บผ่าน Frontend server เพื่อให้ Login และการเรียก API ผ่าน proxy ทำงานครบ

## เปิดระบบในเครื่องที่ติดตั้งแล้ว

เปิด Docker Desktop แล้วรันจาก root repository:

~~~powershell
docker compose up -d
docker compose ps
Start-Process 'http://127.0.0.1:5000/login.html'
~~~

ใช้ `.env` เดิม ไม่ต้องสร้างไฟล์หรือ seed ซ้ำ ข้อมูลเดิมอยู่ใน volume หาก Backend เริ่มใหม่ ต้อง Login ใหม่

## อัปเดตหลังดึงโค้ดใหม่หรือ merge PR

ตรวจไฟล์งานก่อน หากมีงานค้างให้เก็บงานนั้นก่อนอัปเดต จากนั้นเลือก branch Sprint 1 และดึงโค้ดล่าสุด:

~~~powershell
git status
git switch integration/sprint1
git pull --ff-only
~~~

จากนั้นเลือกวิธีอัปเดตแบบใช้สคริปต์:

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1
docker compose up -d --build frontend
docker compose ps
~~~

หรือใช้คำสั่ง Docker Compose โดยตรง รันทีละคำสั่งและทำต่อเมื่อคำสั่งก่อนหน้าสำเร็จ:

~~~powershell
docker compose build backend frontend
docker compose up -d --wait sqlserver
docker compose exec -T sqlserver sh -c 'SQLCMDPASSWORD="$MSSQL_SA_PASSWORD" /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C -b -i /docker-entrypoint-initdb.d/init.sql'
docker compose run --rm --no-deps backend python -m app.init_db
docker compose up -d backend frontend
docker compose ps
~~~

ตรวจ Backend หลังอัปเดต:

~~~powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/' -TimeoutSec 5
~~~

ขั้นตอนนี้ build โค้ดใหม่และสร้างตารางที่ขาด โดยไม่ลบข้อมูลเดิม ไม่ต้อง seed ซ้ำ หากใช้ชุดทดสอบพอร์ต 25001 ให้ใช้คำสั่งในหัวข้อชุดทดสอบแยกแทน

## เปลี่ยนโหมด Login หรือค่า Session

เปิด `.env`:

~~~powershell
notepad .env
~~~

- Login จริง: ตั้ง `TU_API_MODE=real` พร้อม `TU_API_URL` และ `TU_API_KEY`
- Login mock: ตั้ง `TU_API_MODE=mock`
- อายุ Session: ตั้ง `AUTH_SESSION_TTL_SECONDS` เป็นจำนวนวินาทีที่มากกว่า 0 ค่าเริ่มต้นคือ `28800` หรือ 8 ชั่วโมง

หลังแก้ `.env` ให้สร้าง Backend container ใหม่เพื่อรับค่า:

~~~powershell
docker compose up -d --force-recreate backend
~~~

บัญชีต่อไปนี้ใช้เฉพาะ `TU_API_MODE=mock` ไม่ใช่บัญชี TU จริง:

| รหัสนักศึกษา | รหัสผ่าน | ชื่อที่แสดง |
|---|---|---|
| `6800000000` | `0000000000000` (เลขศูนย์ 13 ตัว) | Student User |

ผู้ใช้ที่ Login สำเร็จถูกเก็บใน SQL Server ส่วน token เก็บในหน่วยความจำของ Backend ปุ่ม Logout ยกเลิก token และการเริ่ม Backend ใหม่ทำให้ต้อง Login ใหม่

## ใช้ชุดทดสอบแยกพอร์ต 25001

ชุดนี้ใช้ Compose project `cs261-task60-test` และ volume `cs261-task60-test_sqlserver_data` แยกจากชุดปกติ ใช้ชุดนี้เมื่อต้องการข้อมูลทดสอบเดิมของ Task60 หรือเมื่อพอร์ตชุดปกติถูกใช้งานอยู่

เตรียม `.env` ตามหัวข้อเครื่องใหม่ก่อน บนเครื่องที่มีฐานข้อมูลชุดนี้อยู่แล้ว ให้ใช้รหัสผ่าน SQL Server เดิม การ clone ไปเครื่องใหม่ไม่ได้คัดลอกข้อมูลใน volume จากเครื่องเก่า

### 1. สร้าง override และกำหนดคำสั่ง

ใช้ Docker Compose ที่รองรับ `!override` สร้าง override ใน OS Temp:

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

$composeArgs = @(
    '-p', 'cs261-task60-test',
    '-f', 'compose.yaml',
    '-f', $overridePath
)
~~~

เปิด PowerShell ใหม่ต้องกำหนด `$overridePath` และ `$composeArgs` ใหม่ หากไฟล์ Temp ถูกล้าง ให้สร้าง override ใหม่ด้วย

### 2. สร้างครั้งแรกหรืออัปเดตโค้ด

ไม่ใช้ `scripts/start-backend.ps1` สำหรับชุดนี้ เพราะสคริปต์ใช้ชุดปกติและตรวจ Backend ที่พอร์ต 8000 ให้รันทีละคำสั่ง และทำขั้นถัดไปเมื่อคำสั่งก่อนหน้าสำเร็จ:

~~~powershell
docker compose @composeArgs build backend frontend
docker compose @composeArgs up -d --wait sqlserver
docker compose @composeArgs exec -T sqlserver sh -c 'SQLCMDPASSWORD="$MSSQL_SA_PASSWORD" /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C -b -i /docker-entrypoint-initdb.d/init.sql'
docker compose @composeArgs run --rm --no-deps backend python -m app.init_db
docker compose @composeArgs up -d backend frontend
docker compose @composeArgs ps
~~~

หากสร้างฐานข้อมูลชุดนี้เป็นครั้งแรก ให้เพิ่มรายวิชาและเพิ่มแนวข้อสอบตัวอย่างตามต้องการ หากใช้ฐานข้อมูลเดิม ไม่ต้อง seed ซ้ำ:

~~~powershell
docker compose @composeArgs exec backend python -m scripts.seed_courses --dataset demo --action seed
docker compose @composeArgs exec backend python -m scripts.seed_guides --dataset test --action seed
~~~

### 3. เปิดใช้งานตามปกติ

~~~powershell
docker compose @composeArgs up -d
docker compose @composeArgs ps
Start-Process 'http://127.0.0.1:25001/login.html'
~~~

| บริการชุดทดสอบ | ที่อยู่ |
|---|---|
| หน้า Login | http://127.0.0.1:25001/login.html |
| Backend health | http://127.0.0.1:28001/ |
| API docs | http://127.0.0.1:28001/docs |
| SQL Server | `localhost,21434` |

หลังแก้ `.env` ของชุดนี้ ใช้คำสั่งต่อไปนี้แทนคำสั่งชุดปกติ:

~~~powershell
docker compose @composeArgs up -d --force-recreate backend
~~~

## ตรวจการใช้งานหลังเริ่มระบบ

1. Login ด้วยบัญชีตามโหมดที่ตั้งไว้ แล้วค้นหา CS261
2. เปิดหน้าวิชา กรองปี ภาคเรียน และช่วงสอบ แล้วเปิดอ่านแนวข้อสอบ หากยังไม่มีข้อมูลให้เผยแพร่รายการก่อน
3. เผยแพร่แนวข้อสอบ ตรวจหน้าอ่าน หน้าวิชา และหน้าแนวข้อสอบของฉันหลัง reload
4. แก้ไขรายการของตนเองและย้ายรายวิชา ตรวจว่าทุกหน้าใช้ข้อมูลล่าสุด
5. บันทึกแนวข้อสอบ เปิดหน้ารายวิชาที่บันทึก แล้วนำออก ตรวจว่าต้นฉบับยังอยู่
6. ทดลองยกเลิกลบและยืนยันลบรายการของตนเอง จากนั้นตรวจว่าเปิดอ่านรายการที่ลบไม่ได้
7. Logout แล้วตรวจว่าเปิดใช้ส่วนที่ต้อง Login ไม่ได้

Login ค้นหารายวิชา อ่าน เผยแพร่ จัดการผลงาน และรายการที่บันทึกเชื่อม API แล้ว ระบบรีวิวคะแนนยังอยู่ใน Sprint 2 ขั้นตอนข้างต้นเป็นการตรวจเบื้องต้น ไม่แทนผล UAT ตาม DoD ของแต่ละ U

## ดู Log และหยุดระบบ

ชุดปกติ:

~~~powershell
docker compose ps
docker compose logs --tail=100 backend frontend
docker compose logs -f backend
~~~

กด `Ctrl+C` เพื่อออกจากการดู Log แล้วหยุดระบบโดยเก็บข้อมูลไว้:

~~~powershell
docker compose down
~~~

ชุดทดสอบแยก ใช้ `$composeArgs` ที่กำหนดไว้:

~~~powershell
docker compose @composeArgs ps
docker compose @composeArgs logs --tail=100 backend frontend
docker compose @composeArgs down
~~~

`down` เก็บ volume และข้อมูลไว้ อย่าใช้ `down -v` เพราะจะลบ volume ฐานข้อมูล

## เอกสารเพิ่มเติม

- [คู่มือ Backend และ Login](docs/U1/runbooks/task16-backend-docker-runbook.md)
- [การตั้งค่า TU API](docs/U1/design/task11-tu-api-verification.md)
- [คู่มือทดสอบ Task60 ด้วย project และ volume แยก](docs/U4/runbooks/task60-docker-runbook.md)
- [ผลทดสอบ UI–API ของ Task60](docs/U4/testing/task60-ui-api-test-report.md)
- [ผลทดสอบ API–DAO ของ Task60](docs/U4/testing/task60-api-dao-test-report.md)
- [ผล System Test ของ Task60](docs/U4/testing/task60-system-test-report.md)
- [ผลทดสอบการลบแนวข้อสอบ Task82](docs/U5/testing/task82-delete-my-guides-test-report.md)
