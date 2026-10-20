# Task48: รายงานเชื่อมรายการและหน้าอ่านแนวข้อสอบ

## ขอบเขต

หน้านี้เชื่อมการค้นหารายวิชากับรายการแนวข้อสอบ ตัวกรอง และหน้าอ่านผ่าน Guide API โดยส่งคำขอผ่าน same-origin proxy ของ frontend ใช้ database ID ในการอ่านข้อมูล และไม่เปลี่ยนโหมดของหน้า upload

รายงานแยกผล UI–API, API–DAO และ System Test บน SQL Server ผ่าน Docker

## รุ่นและสภาพแวดล้อม

| รายการ | ค่า |
|---|---|
| Branch | `feat/task48-list-reading-docker` |
| ฐาน branch | `origin/integration/sprint1` ที่ `49670bb` |
| วันที่ตรวจ | 19 ตุลาคม 2026 |
| ระบบ | Windows, Docker Desktop, SQL Server 2022, frontend และ backend ใน Compose project แยก |
| Test project | `cs261-task48-test` |
| Database | `CS261Group4Dev` ภายใน test project |
| Volume | `cs261-task48-test_sqlserver_data` ซึ่งแยกจาก `cs261-group4_sqlserver_data` |

## ผล UI–API

รันจาก `frontend` ด้วย `npm.cmd test`

ผลจริง: `23 passed`

| กรณี | ผลจริง | สถานะ |
|---|---|---|
| Proxy ส่งต่อ path, query, bearer token และ status ของ Guide API | ผ่าน test doubles | ผ่าน |
| Proxy ปฏิเสธ backend path ที่อยู่นอก read API allowlist | ไม่เรียก backend | ผ่าน |
| Client โหลดรายการและ filter options ด้วย course ID | ผ่าน client test | ผ่าน |
| Client ส่งตัวกรองปี ภาคเรียน และช่วงสอบ | ผ่าน client test | ผ่าน |
| หน้าเลือกวิชาแสดงรายการจาก API และ filtered empty state | ผ่าน page-controller test | ผ่าน |
| หน้าอ่าน resolve วิชาและ guide จาก URL โดยไม่เรียก preview catalog | ผ่าน page-controller test | ผ่าน |
| ไม่มี token และ token หมดอายุ | ตรวจ redirect ไป Login และล้าง token หมดอายุ | ผ่าน |
| เส้นทางอ่าน Guide API ไม่เปลี่ยนเส้นทาง upload | ตรวจ auth, course และ publish API client | ผ่าน |

## ผล API–DAO

รันจาก `backend` ด้วย SQLite fixture แยก:

```powershell
$env:DB_CONNECTION_STRING = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=unused;UID=unused'
$env:TU_API_MODE = 'mock'
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider test/test_read_guide_api.py test/test_read_guide_dao.py -q
```

ผลจริง: `15 passed, 6 subtests passed`

ผลชุดนี้ยืนยัน API–DAO ด้วย SQLite fixture ไม่ใช่ผล SQL Server ผล SQL Server ของ Task48 อยู่ใน System Test ด้านล่าง

## ผล System Test บน Docker

ใช้ Compose project `cs261-task48-test` พร้อม volume ใหม่ของ test project และ ports 21433, 28000, 25000 ไม่ได้ mount หรือแก้ volume `cs261-group4_sqlserver_data` เดิม

ใช้ `test` dataset จาก Task26 และ Task41 ตรวจ seed แล้วได้รายวิชา CS100, CS101, CS102 และ CS261 กับแนวข้อสอบ CS261 จำนวน 3 รายการและ CS102 จำนวน 1 รายการ

Login ด้วยบัญชี mock ใน test environment แล้วตรวจ flow ผ่าน Chrome:

| ID | ขั้นตอน | ผลจริง | สถานะ |
|---|---|---|---|
| ST48-01 | Login ค้นหารายวิชา CS261 แล้วเปิดคลัง | หน้าเลือกวิชาใช้ course ID 4 และแสดง guide จาก SQL Server 3 รายการ | ผ่าน |
| ST48-02 | เลือกปีการศึกษา 2568 | API ส่งผล 2 รายการตรงกับข้อมูล seed | ผ่าน |
| ST48-03 | เพิ่มภาคเรียน 2 ให้ปี 2568 | API ส่งรายการว่าง หน้าเว็บแสดงข้อความไม่พบแนวข้อสอบที่ตรงกับตัวกรอง | ผ่าน |
| ST48-04 | ล้างตัวกรอง | ตัวกรองกลับเป็นทั้งหมดและแสดง 3 รายการ | ผ่าน |
| ST48-05 | เปิดรายการแรก | รายละเอียดตรงกับ guide ID 1 มีผู้สอน ผู้เผยแพร่ จำนวนข้อ และคำแนะนำจาก API | ผ่าน |
| ST48-06 | reload หน้าอ่านและกลับหน้ารายการ | รายละเอียดและตัวกรองปี 2568 ยังตรงกับ URL | ผ่าน |
| ST48-07 | เปิด guide ID 999 | แสดงว่าไม่พบแนวข้อสอบและไม่แทนด้วยรายการอื่น | ผ่าน |

## ข้อจำกัดและสิ่งที่ยังไม่ตรวจ

- Backend filter API รองรับปีการศึกษา ภาคเรียน และช่วงสอบ ส่วนผู้สอนเป็นข้อมูลของรายวิชาในหน้าอ่าน API ไม่มี query filter ผู้สอน จึงไม่ได้เพิ่มตัวกรองที่ backend ไม่รองรับ
- Login ใช้ mock mode ไม่ได้เรียก TU API จริง
- Browser test ใช้ seed data ชุด test ที่เก็บอยู่ใน volume แยกสำหรับทำซ้ำ volume นี้ตั้งใจคงไว้ ไม่มีการลบ database หรือ volume
- รายงานผลนี้ยังไม่หมายความว่า branch ถูก push หรือ merge เข้า integration

## คู่มือและไฟล์ที่เกี่ยวข้อง

- [คู่มือเริ่มระบบและตรวจ Task48](Task48-list-reading-docker-runbook.md)
- [คู่มือ Docker และ backend ของ Task16](../U1/U1_Task16_Backend_Docker_Runbook.md)
- [คู่มือ seed แนวข้อสอบ Task41](Task41-guide-seed-data.md)
- โค้ดและ test ที่เกี่ยวข้องอยู่ใน `frontend/public/js/`, `frontend/src/server.js` และ `frontend/src/*test.js`