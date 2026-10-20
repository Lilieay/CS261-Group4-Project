# Task80: ผล System Test รายการแนวข้อสอบของฉัน

## ผลรวม

ตรวจ flow จริงบน Docker project แยก:

1. Login ด้วยบัญชี mock
2. เปิดหน้า shared-courses.html และโหลดรายการจาก SQL Server ผ่าน /api/my-guides
3. กรอง CS263/ปี 2569 แล้วเปิดรายการ Task80 ID 7
4. ตรวจหน้าอ่านตรงกับวิชา ปี ภาคเรียน ช่วงสอบ หัวข้อ รูปแบบ และจำนวนข้อ
5. กลับหน้าของฉันและ reload; ID 5, 6 และ 7 ยังคงอยู่
6. ตรวจ SQL Server ด้วย SELECT read-only และเทียบ ID/วิชากับหน้าเว็บ

ผล: ผ่านทั้งหมด รายการของ publisher อื่น 4 รายการในฐานทดสอบไม่ปรากฏในหน้า list ของผู้ใช้ปัจจุบัน API/DAO tests ตรวจ unauthorized และ empty result เพิ่มเติมแล้ว

## สภาพแวดล้อมและข้อมูล

- Branch: feat/task80-my-guides-docker
- Compose project: cs261-task60-test
- Database: CS261Group4Dev
- Frontend/Backend/SQL Server: 25001 / 28001 / 21434
- Volume: cs261-task60-test_sqlserver_data (เก็บข้อมูลไว้)
- Guide ที่เพิ่มระหว่างทดสอบ: ID 7, Task80 browser integration 2026-10-19, CS263

รายการ ID 6 อยู่ในฐานก่อนเริ่ม browser check และมี objective count 4,354,347; คงข้อมูลและแสดงค่าตามฐานข้อมูลโดยไม่ cleanup

## ยังไม่ได้ทดสอบ

ไม่ได้ทดสอบผู้ใช้จริงจากบัญชีมหาวิทยาลัย, UAT/PO, การแก้ไขหรือย้ายวิชา (Task81), การลบหรือยกเลิก (Task82) และกรณี UI ที่ backend หยุดระหว่างเปิดหน้า การทดสอบทาง API ครอบคลุม status 401/502 และหน้า list มี error/retry state
