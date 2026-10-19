# Task60: U4 — รายงานทดสอบ UI–API การเผยแพร่บน Docker

## ข้อมูลการทดสอบ

| รายการ | รายละเอียด |
|---|---|
| ผู้ทดสอบ | Codex โดยใช้บัญชี mock สำหรับทดสอบ |
| PO | ยังไม่ได้ตรวจรับ |
| รุ่นโค้ด | 6efc76d บน branch feat/task60-publish-api-docker; ต่อจาก Task48 cfc6489 |
| สภาพแวดล้อม | Windows, Docker Compose, SQL Server 2022, Frontend :25001, Backend :28001, SQL Server :21434 |
| Compose project / volume | cs261-task60-test / cs261-task60-test_sqlserver_data |
| โหมด TU | mock; ไม่ใช้ TU key จริง |

## ขอบเขต

ตรวจหน้า upload.html ตั้งแต่ Login, โหลดรายวิชาผ่าน proxy, เผยแพร่ผ่าน POST /api/guides และเปิดรายละเอียดผ่าน API หลังเผยแพร่ ใช้ Docker SQL Server volume แยกจากฐานข้อมูลหลัก

## กรณีทดสอบ

| รหัส | ข้อมูล | ผลคาดหวัง | ผลจริง/สถานะ | หลักฐาน |
|---|---|---|---|---|
| UIAPI-60-01 | Login → Upload → Publish → Read | 200 → 201 → 200 และหน้าอ่านแสดงข้อมูลตรงกับฟอร์ม | ผ่าน: Login 200, Publish 201, Read 200 | browser ที่ :25001; guide ID 5 |
| UIAPI-60-02 | ส่งฟอร์มโดยเว้นข้อมูลบังคับ | แจ้งช่องที่ต้องแก้และไม่ส่งคำขอเผยแพร่ | ผ่าน: UI แสดงข้อผิดพลาด 7 ช่อง | upload.html ใน browser |
| UIAPI-60-03 | title มีแต่ช่องว่างผ่าน API | ตอบ 422 INVALID_PARAMETERS และระบุ title | ผ่าน | POST ผ่าน frontend proxy |
| UIAPI-60-04 | ไม่มี token | ตอบ 401 AUTH_REQUIRED และไม่สร้างรายการ | ผ่าน | POST ผ่าน frontend proxy |
| UIAPI-60-05 | Backend ใช้งานไม่ได้ | หน้าแจ้งเผยแพร่ไม่สำเร็จและไม่แสดงความสำเร็จ | ยังไม่ได้ทดสอบ | — |
| UIAPI-60-06 | รายการในคลังและอ่านหลัง reload | รายการยังอยู่และแสดงรายละเอียดเดิม | ผ่าน: รายการปรากฏใน CS261 และอ่านได้หลัง reload | browser ที่ :25001; guide ID 5 |

## ผล

- Frontend tests: 25 passed, 0 failed ด้วย npm.cmd test
- Docker browser flow: Login 200, Publish 201, Read 200, List 200; รายการอ่านได้หลัง reload
- UI validation หยุดการเผยแพร่เมื่อเว้นข้อมูลบังคับ
- API ปฏิเสธ title ที่มีแต่ช่องว่างด้วย 422 และปฏิเสธคำขอไม่มี token ด้วย 401
- SQL Server มีรายการทดสอบชื่อ Task60 Docker integration 2026-10-19 เพียงหนึ่งแถว (ID 5); รายละเอียดอยู่ในรายงาน API–DAO

กรณี token หมดอายุ, backend ล่ม, จำนวนข้อผิดพลาดผ่าน API, การเผยแพร่โดยผู้ใช้อื่น และการตรวจรับ PO ยังไม่ได้ทำ
