# Task16: รายงานทดสอบ API กับฐานข้อมูล

## รุ่นและสภาพแวดล้อม

- Source revision: `4e1bd37d1c9ee262f73aa54471d5e2c7a43fec37`
- ชุดทดสอบอัตโนมัติ: Windows, Python 3.14.6, SQLite แยกสำหรับ test
- ทดสอบฐานข้อมูล Docker: SQL Server 2022

## ผลทดสอบอัตโนมัติ

| กรณี | ผลที่คาดหวัง | ผลจริง |
|---|---|---|
| Login สำเร็จ | API ตอบ 200 พร้อม user ID จากฐานข้อมูลและ bearer token | ผ่านใน `backend/test/test_auth.py` |
| Login ซ้ำด้วย username เดิม | คำตอบทั้งสองครั้งมี database user ID เดียวกัน | ผ่านใน `backend/test/test_auth.py` |
| TU ปฏิเสธหรือ provider ใช้งานไม่ได้ | API ตอบ 401 โดยไม่มี token และไม่มี user ใหม่ | ผ่านด้วย TU adapter จริงและ HTTP transport ที่แทนใน test |
| Database ใช้งานไม่ได้หลัง verify | API ตอบ 503 และไม่ออก token | ผ่านด้วย SQLAlchemy failure ที่ฉีดใน test |
| Publisher หลัง login | Guide เก็บ publisher ID เดียวกับ user ID ที่ login สร้าง | ผ่านใน `backend/test/test_publish_guide_api.py` |
| ปฏิเสธการ publish | ไม่สร้าง Guide เพิ่ม และไม่ลบ user ที่ login สร้างไว้ | ผ่านใน `backend/test/test_publish_guide_api.py` |

คำสั่งเต็มและจำนวน test อยู่ใน [สรุปผลตรวจสอบ Backend และ Docker](U1_Task16_Backend_Verification_Report.md)

## การตรวจ SQL Server ใน Docker

| กรณี | ผลที่คาดหวัง | ผลจริง |
|---|---|---|
| Login ซ้ำผ่าน AuthService และ UserDAO จริง | ได้ user row เดียวและ database ID เดิม; logout ผ่าน; service instance ใหม่ปฏิเสธ token เดิม | ผ่าน |
| Restart backend process | Token เก่าถูกปฏิเสธที่ me, status แสดง `logged_in=false`, login ใหม่ใช้ database ID เดิม | ผ่าน; database ID `1002` |
| Storage connection failure | Login ตอบ 503 และไม่มี token ที่ service อ่านกลับได้ | ผ่านใน isolated TestClient probe โดย ODBC connect ไป `127.0.0.1:1` ล้มเหลว; production SQL Server ไม่ได้หยุด |
| Cleanup และตรวจข้อมูลเดิม | ลบเฉพาะ temporary user; user, course และ guide เดิมยังอยู่ | ผ่าน; ก่อนทดสอบมี users 2, courses 24, guides 0 |
| HTTP ผ่าน frontend proxy | Login, status, me, login ซ้ำ และ logout ทำงานตามสัญญา | ผ่าน; login ซ้ำคืน user ID `1002`; me หลัง logout ตอบ 401 |

การตรวจใช้ TU mock และไม่เรียก TU จริง Temporary verification scripts อยู่นอก repository และไม่ถูก commit ห้ามใส่ password หรือ token
