# Task16: รายงานทดสอบ UI กับ API

## รุ่นและสภาพแวดล้อม

- Source revision: `4e1bd37d1c9ee262f73aa54471d5e2c7a43fec37`
- สภาพแวดล้อมที่กำหนด: Windows, Docker Compose, SQL Server 2022, browser ในเครื่อง
- โหมด TU: `mock` ด้วยบัญชี `6800000000` และรหัสผ่าน `0000000000000`
- ผลทดสอบ: Chrome และ HTTP proxy ที่พอร์ต 5000

## กรณีทดสอบ

| กรณี | ผลที่คาดหวัง | ผลจริง |
|---|---|---|
| เข้าสู่ระบบด้วยบัญชี mock | หน้าเว็บเปิดหน้าค้นหารายวิชา และ frontend เขียน bearer token ลง `sessionStorage` ก่อน redirect ตาม source code | Chrome เปลี่ยนไป `courses.html`; ไม่ได้ตรวจค่า `sessionStorage` โดยตรง |
| รหัสผ่านไม่ถูกต้อง | หน้าเว็บแสดงข้อความผิดพลาดทั่วไปและไม่เปิดหน้าหลัง login | Chrome แสดงข้อความผิดพลาดทั่วไป |
| ช่องกรอกว่างหรือ username มีตัวอักษร | หน้าเว็บแสดงข้อผิดพลาดของช่องกรอกและไม่ส่งคำขอ login | Chrome แสดงข้อความ required สำหรับ username และ password ที่ว่าง; username ที่มีตัวอักษรแสดง numeric validation |
| Backend หยุดทำงาน | หน้าเว็บแสดงข้อความผิดพลาดและเปิดใช้งานฟอร์มอีกครั้ง | หลัง `docker compose stop backend`, Chrome แสดงข้อความทั่วไปและเปิดใช้ช่องกรอกกับปุ่มอีกครั้ง; หลังเริ่ม backend และ readiness ผ่าน การ retry สำเร็จ |
| `status`, `me`, และ `logout` ผ่าน proxy | Status และ me ตอบ 200; หลัง logout คำขอ me เดิมตอบ 401 | HTTP proxy: login/status/me/logout ผ่าน; login ซ้ำคืน ID `1002`, me หลัง logout ตอบ 401 |
| Token หลัง restart backend | Token เก่าถูกปฏิเสธ; status แสดงว่าไม่ได้ login; login ใหม่ใช้ database ID เดิม | ผ่าน: me ตอบ 401, status เป็น `logged_in=false`, login ใหม่คืน ID `1002` |

## ขอบเขตหลักฐาน

Chrome ใช้ mock provider และไม่เรียก TU จริง การตรวจไม่อ่าน browser storage โดยตรง ข้อความเรื่อง `sessionStorage` อ้างอิง source code เท่านั้น การ redirect ไป `courses.html` ไม่ยืนยันว่าเนื้อหา preview หรือการควบคุมสิทธิ์ในหน้านั้นเชื่อมกับ session จริง ห้ามบันทึก password หรือ access token
