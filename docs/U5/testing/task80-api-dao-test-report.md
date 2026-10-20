# Task80: ผลทดสอบ API–DAO รายการแนวข้อสอบของฉัน

## เส้นทางข้อมูล

Frontend เรียก GET /api/my-guides พร้อม Bearer token ผ่าน frontend/src/server.js proxy ซึ่งส่งต่อไปยัง Backend path ตายตัว /api/my-guides จากนั้น FastAPI ใช้ current_user หา username ที่ผ่าน Login แล้วเรียก MyGuideDAO.list_by_username() เพื่อกรอง Guide.publisher และ eager-load รายวิชา

DTO เป็น array แบบ flat มี course, ปี/ภาคเรียน, ช่วงสอบ, รูปแบบ, จำนวนข้อ, หัวข้อ และคำแนะนำ โดยไม่รับ owner จาก query หรือ body ของ browser

## ผลทดสอบ

| ชั้น | ผลจริง | สถานะ |
|---|---|---|
| Frontend proxy | ส่ง Authorization/Accept, ปิด cache, จำกัด backend path, รักษา 401/error และตอบ 502 เมื่อเชื่อมต่อไม่ได้ | ผ่าน |
| GuideApi client | แปลง flat DTO, รักษาค่า null/ศูนย์, รองรับ [] และปฏิเสธ DTO เสีย | ผ่าน |
| Backend API tests | 4 tests ผ่าน: รายการเจ้าของ, ไม่มี token, token ผิด, ผู้ใช้ที่ไม่มีรายการได้ [] | ผ่าน |
| DAO SQLite tests | 4 tests ผ่าน | ผ่าน |
| DAO SQL Server tests | 4 tests ผ่านใน schema task68_test_<uuid> และยืนยัน rollback ลบ schema ทดสอบ | ผ่าน |
| SQL Server project test | SELECT แบบอ่านอย่างเดียวพบ ID 5, 6, 7 ของผู้ใช้ปัจจุบัน และ publisher อื่น 4 รายการ | ผ่าน |

SQL Server test ใช้ Compose project cs261-task60-test และฐานข้อมูล CS261Group4Dev ผ่าน Backend container เพื่อใช้ driver/network ของ Docker ชุด DAO สร้าง schema แยกใน transaction; ไม่มีการแก้แถวใน schema แอปพลิเคชัน

รัน API tests ในเครื่องจาก backend:

    .\.venv\Scripts\python.exe -m pytest -q test/test_my_guides_api.py

รัน DAO tests บน SQL Server โดย mount backend/test แบบ read-only ใน one-off backend container และตั้ง TASK68_TEST_SQLSERVER=1 ห้ามใช้ SQLite result แทนผล SQL Server
