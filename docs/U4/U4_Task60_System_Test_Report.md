# Task60: U4 — รายงาน System Test การเผยแพร่บน Docker

## ข้อมูลการทดสอบ

| รายการ | รายละเอียด |
|---|---|
| รุ่นโค้ด | 6efc76d บน branch feat/task60-publish-api-docker |
| Services | sqlserver, backend, frontend จาก Docker Compose |
| Compose project / volume | cs261-task60-test / cs261-task60-test_sqlserver_data |
| URL | Frontend http://127.0.0.1:25001, Backend http://127.0.0.1:28001, SQL Server 127.0.0.1:21434 |
| ฐานข้อมูล | CS261Group4Dev บน SQL Server 2022 |

## ตารางผล

| รหัส | ผลคาดหวัง | ผลจริง/สถานะ | หลักฐาน |
|---|---|---|---|
| SYS-60-01 | Login → เผยแพร่ → เปิดอ่านครบเส้นทาง | ผ่าน: Login 200, Publish 201, Read 200 | browser flow จาก upload.html ไป read-courses.html |
| SYS-60-02 | รายการแสดงในคลังรายวิชาและยังอ่านได้หลัง reload | ผ่าน: พบรายการใน CS261 และเปิดอ่านซ้ำหลัง reload | browser list/read; guide ID 5 |
| SYS-60-03 | ผู้ใช้อื่นอ่านรายการได้ตามสิทธิ์ | ยังไม่ได้ทดสอบด้วยบัญชีคนที่สอง | — |
| SYS-60-04 | ข้อมูลไม่ครบหรือไม่ถูกต้องต้องไม่เผยแพร่ | ผ่าน: UI แจ้งช่องบังคับ; API ปฏิเสธ title ว่างด้วย 422; ไม่มี token ได้ 401 | browser validation และ API proxy |
| SYS-60-05 | การส่งซ้ำไม่สร้างรายการทดสอบซ้ำ | ผ่านเฉพาะการส่งผ่าน UI หนึ่งครั้ง: SQL พบชื่อทดสอบหนึ่งแถว; ไม่ได้ replay POST ที่ถูกต้อง | SQL query; guide ID 5 |
| SYS-60-06 | Backend/Database ล้มเหลวต้องแจ้งผิดพลาดและไม่มีข้อมูลค้าง | ยังไม่ได้จำลอง | — |

## สถานะ

เส้นทางหลัก UI → API → SQL Server และการอ่านหลัง reload ผ่านบน Docker ด้วย volume ทดสอบแยก เหลือทดสอบ error ระหว่างบันทึก, ผู้ใช้อื่น และ PO ตรวจรับก่อนถือว่า UAT เสร็จ
