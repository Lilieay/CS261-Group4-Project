# Task80: ผลทดสอบ UI–API รายการแนวข้อสอบของฉัน

## ขอบเขต

ตรวจหน้า shared-courses.html ตั้งแต่ Login, โหลดรายการของผู้ใช้ปัจจุบัน, ค้นหา/กรอง, เปิดอ่าน, กลับหน้ารายการ และ reload โดยใช้ GET /api/my-guides ผ่าน same-origin proxy

## ผลทดสอบ

| กรณี | ผลจริง | สถานะ |
|---|---|---|
| Login ด้วยบัญชี mock ใน Docker project ทดสอบ | เปิดหน้าค้นหารายวิชาได้; โปรไฟล์แสดงผู้ใช้ที่ Login | ผ่าน |
| เปิดหน้าแนวข้อสอบของฉัน | แสดง 3 รายการที่ API คืนจาก SQL Server | ผ่าน |
| กรองวิชา CS263 และปี 2569 | เหลือรายการ Task80 ID 7 รายการเดียว | ผ่าน |
| เปิดรายการ ID 5 จากหน้า list | URL ส่ง course CS261, courseId 4, guide 5 และ source=api; หน้าอ่านแสดงข้อมูลตรงกับ SQL Server | ผ่าน |
| กลับหน้าแนวข้อสอบของฉันและ reload | รายการทั้ง 3 ยังคงโหลดจาก API | ผ่าน |
| เผยแพร่รายการผ่าน upload UI | สร้าง Task80 ID 7 ใน CS263 ปี 2569 ภาค 1 ปลายภาค แบบผสม 2 อัตนัย + 3 ปรนัย | ผ่าน |
| รายการว่าง / API error / retry | แยก empty state จาก error; ปุ่ม retry โหลดใหม่ได้ | ผ่านใน page tests |

Browser integration ใช้ Compose project cs261-task60-test, Frontend 127.0.0.1:25001, Backend 127.0.0.1:28001 และ SQL Server 127.0.0.1:21434 ข้อมูลทดสอบที่สร้างเพิ่มคือ guide ID 7 และเก็บไว้ใน volume ทดสอบ

SQL Server read-only query ยืนยันรายการของผู้ใช้ 6800000000 เป็น ID 5 (CS261), ID 6 (CS100) และ ID 7 (CS263) โดยมีรายการของ publisher อื่นอีก 4 รายการซึ่งไม่ปรากฏในหน้า “ของฉัน” ID 6 มีจำนวนปรนัย 4,354,347 ตามข้อมูลในฐานข้อมูล และหน้าแสดงค่าที่ API คืนโดยตรง

npm.cmd test ผ่าน 34 กรณี รวม proxy, DTO, loading/error/empty/retry, search/filter, course ที่ไม่มีใน preview catalog, read navigation และการปฏิเสธ external returnTo

## ข้อจำกัด

ทดสอบ browser ด้วยบัญชี mock ที่มีให้หนึ่งบัญชี; การแยกเจ้าของสองบัญชีตรวจผ่าน DAO/API fixtures และ SQL Server query ไม่ได้สร้าง auth bypass หรือแก้ข้อมูลผู้ใช้รายอื่น ส่วนการตรวจ SQL Server ทำด้วย query แบบอ่านอย่างเดียวและ DAO test schema ชั่วคราว
