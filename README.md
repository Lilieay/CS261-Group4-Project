# CS261-Group4-Project

โครงการวิชา CS261 กลุ่ม 4: เว็บแบ่งปันแนวข้อสอบและสรุปรายวิชา CS สำหรับนักศึกษามหาวิทยาลัยธรรมศาสตร์

## สถานะโปรเจกต์

ปัจจุบันเป็นโครงการตั้งต้นสำหรับเริ่มพัฒนาฟีเจอร์

| ส่วน | เทคโนโลยี | สถานะ |
| --- | --- | --- |
| Frontend | Node.js + Express + HTML/CSS/JavaScript | เสิร์ฟไฟล์จาก `public` และมีปุ่มทดสอบ JavaScript |
| Backend | Python + FastAPI | มี `GET /` สำหรับตรวจว่า backend ทำงาน |
| Database | Microsoft SQL Server + SQLAlchemy | ยังต้องเตรียมการเชื่อมต่อ |
| Login | TU API | ยังต้องพัฒนา |
| Docker | Frontend, Backend และ SQL Server รวม 3 containers | ยังต้องเตรียมใน Task3 |

Task2 ยังต้องเติม config ตัวอย่างและผลทดสอบการเชื่อม SQL Server ผ่าน SQLAlchemy ก่อนนับว่าเสร็จ

## เครื่องมือที่ต้องมี

- Git
- Node.js 24.x พร้อม npm
- Python 3.14.x

คำสั่งในเอกสารนี้ใช้ Windows PowerShell และรันจากโฟลเดอร์รากของ repo เว้นแต่จะระบุไว้ต่างหาก
เวอร์ชันที่ตรวจบนเครื่องผู้พัฒนา: Node.js `24.18.0`, Python `3.14.6` และ Git `2.51.0`
ทีมควรใช้เวอร์ชันเดียวกันระหว่างเริ่มงาน โดย dependencies ของ Python ยังไม่ได้ล็อกเวอร์ชัน

## ดาวน์โหลดและติดตั้ง

```powershell
git clone --branch integration/sprint1 https://github.com/Lilieay/CS261-Group4-Project.git
cd CS261-Group4-Project
```

คำสั่งนี้เลือก branch พัฒนาของ Sprint 1 เพื่อให้ได้โค้ดตั้งต้นและคู่มือที่ทีมแชร์ไว้
ถ้ามี repo ในเครื่องแล้ว ให้เลือก `integration/sprint1` ตาม [คู่มือ Git](docs/GIT_WORKFLOW.md) ก่อนเริ่มติดตั้งด้านล่าง

### Frontend

```powershell
npm --prefix frontend ci
```

`npm ci` ติดตั้งตาม `frontend/package-lock.json` ที่ทีม commit ไว้
เมื่อเพิ่ม dependency ใหม่ ให้ใช้ `npm --prefix frontend install <package-name>` และ commit ทั้ง `package.json` กับ `package-lock.json`

### Backend

```powershell
python -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

ใช้ Python จาก virtual environment โดยตรง จึงไม่ต้อง activate และไม่ต้องเปลี่ยน execution policy ของ PowerShell

## เริ่มระบบ

เปิด terminal สองหน้าต่าง โดยทั้งสองหน้าต่างอยู่ที่ราก repo

### Terminal 1: Frontend

```powershell
npm --prefix frontend start
```

เปิด [Frontend](http://127.0.0.1:5000/) ใน browser
Express เสิร์ฟ `frontend/public/index.html` ที่ `/` และเสิร์ฟ CSS/JS ตาม path ของไฟล์ เช่น `/css/styles.css` และ `/js/script.js`

### Terminal 2: Backend

```powershell
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

- [Backend](http://127.0.0.1:8000/) ต้องตอบ `{"message":"Backend is running"}`
- [Swagger UI](http://127.0.0.1:8000/docs) ใช้ดูและทดลอง API

ทั้งสองคำสั่งต้องรันค้างไว้เพื่อรับ request ใช้ `Ctrl+C` เมื่อต้องการหยุด
ตอนนี้ frontend และ backend ยังเป็นตัวอย่างที่รันแยกกัน ยังไม่ได้เชื่อม Login หรือฐานข้อมูล

## ตรวจว่า setup ทำงาน

1. เปิด frontend แล้วเห็นข้อความสีน้ำเงินขนาดใหญ่
2. กดปุ่มทดสอบแล้วข้อความเปลี่ยนเป็น `javascript active`
3. ใน browser DevTools > Network ตรวจว่า CSS และ JavaScript โหลดสำเร็จ
4. เปิด backend แล้วได้ JSON ตามตัวอย่างด้านบน
5. เปิด Swagger UI แล้วเห็น endpoint `GET /`

การตรวจชุดนี้เป็น smoke check ของโครงการตั้งต้น ยังไม่ใช่ผลทดสอบ Login หรือการเชื่อมฐานข้อมูล
เมื่อแก้ HTML/CSS/JS ใน `public` ให้บันทึกแล้ว refresh browser; เมื่อแก้ `frontend/src/server.js` ให้หยุดและเริ่ม frontend ใหม่

## โครงสร้างหลัก

```text
CS261-Group4-Project/
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── src/server.js       # Express server
│   └── public/             # HTML, CSS, JavaScript และ assets ที่ browser ใช้
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── routers/        # API endpoints
│   │   ├── schemas/        # รูปแบบ request/response
│   │   ├── services/       # กติกาและขั้นตอนของฟีเจอร์
│   │   ├── models/         # Entities และแบบข้อมูล
│   │   └── dao/            # การเข้าถึงฐานข้อมูล
│   └── test/               # ที่เตรียมไว้สำหรับ tests
└── docs/                   # เอกสารของทีม
```

บางโฟลเดอร์ยังมีเพียง placeholder; ให้เพิ่มโค้ดตาม task ที่รับผิดชอบ

## การทำงานร่วมกันด้วย Git

สำหรับรอบส่งมอบ ใช้ `main` เก็บเวอร์ชันที่ผ่าน integration/UAT และพร้อม Demo
พัฒนาแต่ละชุดงานบน branch ของตัวเอง แล้วรวมผ่าน PR เข้า `integration/sprint1` ก่อน เช่น:

- `feat/task5-login-ui` สำหรับหน้า Login ฝั่ง frontend
- `feat/task6-login-api` สำหรับ Login API ฝั่ง backend
- `feat/task7-user-dao` สำหรับ User Entity/DAO
- `chore/task3-docker` สำหรับ Docker
- `docs/task2-setup-guide` สำหรับเอกสาร setup

แตก branch งานจาก integration branch ล่าสุด เมื่อ task พร้อมให้เพื่อน review แล้ว merge เข้า integration branch
ทำ task integration เพื่อทดสอบ frontend/backend/database ร่วมกัน เมื่อผ่านเกณฑ์ส่งมอบจึงเปิด PR จาก integration branch เข้า `main`
ใช้ tag เช่น `v0.1.0` ระบุเวอร์ชัน Demo 1 และ `v0.2.0` ระบุ Demo 2 โดย Sprint ถัดไปใช้ `integration/sprint2`
ปัจจุบัน `main` ยังเป็นโครงการตั้งต้นตามสถานะด้านบน ยังไม่ได้ผ่านเกณฑ์ Demo ของฟีเจอร์

ประเภทงานที่ใช้บ่อย:

| Type | ความหมาย |
| --- | --- |
| `feat` | เพิ่มฟีเจอร์ เช่น หน้า Login หรือ API ใหม่ |
| `fix` | แก้บั๊ก เช่น ปุ่มไม่ทำงาน หรือโหลด CSS ไม่ได้ |
| `chore` | เตรียมและดูแลโปรเจกต์ เช่น `.gitignore` หรือ config เครื่องมือ |
| `docs` | เขียนหรือแก้เอกสาร เช่น README และคู่มือ Git |

ชื่อ branch ใช้ `<type>/<task>-<short-description>` ส่วนข้อความ commit ใช้ `<type>(<scope>): <description>` เช่น:

```powershell
git switch integration/sprint1
git pull --ff-only origin integration/sprint1
git switch -c feat/task5-login-ui
git commit -m "feat(task5): add login form and validation"
```

ตัวอย่างนี้ใช้หลังทีมเตรียม integration branch แล้ว ส่วน commit ต้องใช้หลังจากแก้ ทดสอบ และ stage ไฟล์ของงาน; `scope` เช่น `task5` บอกงานที่เกี่ยวข้อง
อ่านการเตรียม integration branch ความหมายประเภทงาน รูปแบบ commit และคำสั่งตั้งแต่แตก branch จนรวมงานและติด tag ใน [คู่มือ Git ของทีม](docs/GIT_WORKFLOW.md)

## ปัญหาที่อาจพบระหว่างรัน

| อาการ | วิธีตรวจและแก้ |
| --- | --- |
| หน้าเว็บแสดงรายชื่อโฟลเดอร์ทั้ง repo | ตรวจว่า URL เป็น `http://127.0.0.1:5000/` และเริ่ม Express ด้วย `npm start`; VS Code Live Preview เป็นอีก server หนึ่ง |
| เปลี่ยนไฟล์แล้ว browser ยังแสดงผลเดิม | บันทึกไฟล์และกด `Ctrl+Shift+R` |
| ปุ่มไม่ทำงาน | เปิด DevTools > Console และตรวจว่าใช้ `document.getElementById` พร้อม `id` ที่ตรงกับ HTML |
| Frontend พิมพ์ URL แล้วจบทันที | ตรวจว่าพอร์ตว่างและตรวจ error ใน callback ของ `app.listen`; Express 5 เรียก callback เมื่อเกิด error ได้ด้วย |
| Backend แจ้งว่าไม่พบ `fastapi` หรือ `uvicorn` | ติดตั้ง requirements และรันด้วย Python ใน `backend/.venv` ตามคำสั่งด้านบน |
