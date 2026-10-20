# Task72: U5 — API แก้ไขแนวข้อสอบของฉัน

## API และสิทธิ์เจ้าของ

`PUT /api/my-guides/{guide_id}` ใช้ `current_user` ตัวตรวจ Login เดิมและรับ Bearer token เท่านั้น API ใช้ username จาก session ที่ยืนยันแล้วค้น `users.id` ในฐานข้อมูล จากนั้น `UpdateOwnedGuideDAO.update_owned()` อัปเดตโดยกรองทั้ง `guides.id` และ `guides.publisher_id` ผู้ใช้ที่ไม่ใช่เจ้าของและรายการที่ไม่มีอยู่ตอบ `404 GUIDE_NOT_FOUND` เหมือนกัน

Request DTO ตรวจข้อมูลบังคับตาม U5/U3, ตัดช่องว่างหัวท้ายของชื่อและหัวข้อ, จำกัดค่าภาคเรียน/ช่วงสอบ/รูปแบบข้อสอบ, ปฏิเสธจำนวนข้อที่ไม่เป็นบวก และตรวจว่า course มีอยู่ก่อนแก้ข้อมูล การเปลี่ยนวิชาแก้ row เดิมโดยคง `id` และ `publisher_id`; API commit เมื่อสำเร็จและ rollback เมื่อเกิด SQLAlchemy error ไม่มีการเพิ่ม Entity, table หรือ column

Response `MyGuideUpdateResponse` คืนข้อมูลรายการที่แก้ไขแล้วพร้อมชื่อและรหัสวิชาที่ update ล่าสุด

## Test cases และผล

ใช้ SQLite in-memory ผ่าน FastAPI `TestClient`; แต่ละกรณีสร้าง fixture ใหม่และ rollback outer transaction หลังจบ test ไม่มีการเชื่อมต่อหรือแก้ข้อมูลในฐานข้อมูลจริง

| รหัส | ข้อมูลทดสอบ | ผลคาดหวัง | ผลจริง | ผ่าน/ไม่ผ่าน | หลักฐาน |
|---|---|---|---|---|---|
| T72-API01 | เจ้าของส่งข้อมูลครบและเปลี่ยน CS261 เป็น CS262 | `200`; คง ID/เจ้าของเดิม, คืนข้อมูลใหม่, ไม่สร้าง row ซ้ำ | `200`; ID และ publisher คงเดิม, course เป็น CS262, จำนวน row เท่าเดิม | ผ่าน | `test_owner_can_update_guide_and_move_it_to_another_course` |
| T72-API02 | PUT ไม่มี Authorization header | `401`; ไม่แก้ข้อมูล | `401` จาก `current_user` | ผ่าน | `test_update_requires_login` |
| T72-API03 | PUT ด้วย token ที่ไม่ถูกต้อง | `401`; ไม่แก้ข้อมูล | `401` จาก `current_user` | ผ่าน | `test_update_rejects_invalid_token` |
| T72-API04 | ผู้ใช้ที่ Login แล้วส่ง ID รายการของผู้อื่น | `404 GUIDE_NOT_FOUND`; ข้อมูลเดิมคงเดิม | `404`; snapshot ของรายการไม่เปลี่ยน | ผ่าน | `test_non_owner_cannot_update_another_users_guide` |
| T72-API05 | เจ้าของส่ง ID ที่ไม่มีในระบบ | `404 GUIDE_NOT_FOUND` | `404 GUIDE_NOT_FOUND` | ผ่าน | `test_missing_guide_returns_not_found` |
| T72-API06 | ชื่อเป็นช่องว่างล้วน | `422`; ไม่แก้ข้อมูล | `422`; snapshot คงเดิม | ผ่าน | `test_invalid_data_returns_422_and_preserves_guide[blank-title]` |
| T72-API07 | หัวข้อเป็นช่องว่างล้วน | `422`; ไม่แก้ข้อมูล | `422`; snapshot คงเดิม | ผ่าน | `test_invalid_data_returns_422_and_preserves_guide[blank-topics]` |
| T72-API08 | จำนวนปรนัยเป็น `-1` | `422`; ไม่แก้ข้อมูล | `422`; snapshot คงเดิม | ผ่าน | `test_invalid_data_returns_422_and_preserves_guide[negative-count]` |
| T72-API09 | `course_id` ที่ไม่มีอยู่ | `422 COURSE_NOT_FOUND`; ไม่แก้ข้อมูล | `422`; snapshot คงเดิม | ผ่าน | `test_invalid_data_returns_422_and_preserves_guide[unknown-course]` |
| T72-API10 | `semester=4` | `422`; ไม่แก้ข้อมูล | `422`; snapshot คงเดิม | ผ่าน | `test_invalid_data_returns_422_and_preserves_guide[invalid-semester]` |
| T72-API11 | `exam_period=quiz` | `422`; ไม่แก้ข้อมูล | `422`; snapshot คงเดิม | ผ่าน | `test_invalid_data_returns_422_and_preserves_guide[invalid-exam-period]` |
| T72-API12 | รูปแบบข้อสอบไม่อยู่ในค่าที่กำหนด | `422`; ไม่แก้ข้อมูล | `422`; snapshot คงเดิม | ผ่าน | `test_invalid_data_returns_422_and_preserves_guide[invalid-format]` |
| T72-API13 | รูปแบบปรนัยแต่ส่ง `subjective_count` | `422`; ไม่แก้ข้อมูล | `422`; snapshot คงเดิม | ผ่าน | `test_invalid_data_returns_422_and_preserves_guide[incompatible-count]` |
| T72-API14 | จำลอง SQLAlchemy error ระหว่าง update | `500 GUIDE_UPDATE_FAILED`; rollback และไม่รายงานสำเร็จ | `500`; fixture snapshot คงเดิมหลัง rollback | ผ่าน | `test_database_error_returns_500_and_preserves_guide` |

คำสั่งรันจาก `backend` (หากไม่มี `backend/.env` ให้กำหนดค่า placeholder ชั่วคราว เนื่องจาก `app.config` ต้องการ `DB_CONNECTION_STRING` ตอน import; API tests สร้าง SQLite in-memory เองและไม่ได้ใช้ connection string นี้):

```powershell
$env:DB_CONNECTION_STRING='DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=unused;Trusted_Connection=yes;TrustServerCertificate=yes'
$env:PYTHONPATH='.'
.venv\Scripts\python.exe -m pytest -q test/test_my_guide_updates_api.py
Remove-Item Env:DB_CONNECTION_STRING
Remove-Item Env:PYTHONPATH
```

ผลที่รัน: `14 passed` (0.79s). มีคำเตือน deprecation จาก Starlette เรื่อง `httpx`/`httpx2`; ไม่มี test failure

## Postman และการคืนข้อมูล

Collection อยู่ที่ `backend/postman/Task72-my-guides-update.postman_collection.json` ใช้ตัวแปร `baseUrl`, `accessToken`, `guideId`, `courseId` และไม่มี username/password/token จริง ผู้ใช้ต้องเติม token และ ID ใน Postman environment/local variables ก่อนส่ง request

API test ใช้ข้อมูล in-memory แยกต่อ test และ rollback outer transaction/ปิด Session หลังจบ จึงไม่มีข้อมูลที่ต้องลบคืนจาก SQL Server หรือฐานข้อมูลของแอป
