# Task73: API ลบแนวข้อสอบของตนเอง

## ขอบเขตและการตั้งค่า

- Endpoint: `DELETE /api/my-guides/{guide_id}`
- ใช้ dependency `current_user` จากระบบ Login เดิม และตรวจเจ้าของจากผู้ใช้ที่ยืนยันตัวตนแล้ว
- ลบด้วย `DeleteOwnedGuideDAO` ซึ่งกรองทั้งรหัสแนวข้อสอบและ `publisher_id`
- สำเร็จตอบ HTTP 200 พร้อม DTO ที่มีรหัสรายการและข้อความยืนยัน
- ไม่พบรายการหรือรายการไม่ใช่ของผู้ใช้ตอบ HTTP 404 เดียวกัน เพื่อไม่เปิดเผยรายการของผู้อื่น
- การทดสอบ API ใช้ SQLite in-memory แยกจากฐานข้อมูลจริง ไม่มีการเพิ่มตารางหรือข้อมูลถาวร
- Postman Collection ใช้ตัวแปร `{{username}}`, `{{password}}` และ `{{accessToken}}` โดยไม่มี credential หรือ token จริงฝังในไฟล์

## ผลการทดสอบ

คำสั่งที่รันจาก `backend`:

```powershell
$env:DB_CONNECTION_STRING='DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=unused;Trusted_Connection=yes;TrustServerCertificate=yes'
.venv\Scripts\python.exe -m pytest test/test_my_guide_deletions_api.py -q
```

ค่าการเชื่อมต่อข้างต้นใช้เพื่อให้โมดูล config โหลดได้เท่านั้น การทดสอบสร้าง SQLite in-memory และไม่ได้เชื่อมต่อ SQL Server

| รหัส | ข้อมูลทดสอบ | ผลคาดหวัง | ผลจริง | สถานะ/หลักฐาน |
|---|---|---|---|---|
| API73-01 | เจ้าของลบรายการที่ตนเป็นเจ้าของด้วย token ที่ Login สำเร็จ | HTTP 200, ได้ DTO ยืนยัน และรายการถูกลบ | HTTP 200; ได้ `id` และข้อความยืนยัน; รายการหายจาก SQLite | ผ่าน — `test_owner_can_delete_guide_and_receives_confirmation` |
| API73-02 | ลบโดยไม่ส่ง token | HTTP 401 และข้อมูลไม่ถูกลบ | HTTP 401 จาก `current_user` | ผ่าน — `test_delete_requires_login` |
| API73-03 | ส่ง token ที่ไม่ถูกต้อง | HTTP 401 และข้อมูลไม่ถูกลบ | HTTP 401 จาก `current_user` | ผ่าน — `test_delete_rejects_invalid_token` |
| API73-04 | ผู้ใช้ที่ Login แล้วพยายามลบรายการของผู้ใช้อื่น | HTTP 404 และรายการเดิมยังอยู่ | HTTP 404 `GUIDE_NOT_FOUND`; รหัสรายการไม่เปลี่ยน | ผ่าน — `test_non_owner_cannot_delete_another_users_guide` |
| API73-05 | ลบรหัสรายการที่ไม่มีอยู่ | HTTP 404 และข้อมูลอื่นยังอยู่ | HTTP 404 `GUIDE_NOT_FOUND`; ข้อมูลเดิมยังอยู่ | ผ่าน — `test_missing_guide_returns_not_found_without_changing_data` |
| API73-06 | รหัสรายการเป็น 0 หรือค่าติดลบ | HTTP 422 และไม่ลบข้อมูล | HTTP 422 `GUIDE_ID_INVALID` ทั้งสองค่า | ผ่าน — `test_invalid_guide_id_returns_422` (2 sub-cases) |
| API73-07 | DAO จำลองให้เกิด SQLAlchemyError ระหว่างลบ | HTTP 500 และข้อมูลเดิมยังอยู่ | HTTP 500 `GUIDE_DELETE_FAILED`; ข้อมูลเดิมยังอยู่ | ผ่าน — `test_database_error_returns_500_and_preserves_data` |

หลักฐานรวมจาก pytest: `8 passed, 1 warning in 0.71s` คำเตือนเป็น Starlette แจ้งว่า `httpx` ใน TestClient จะเลิกใช้ในอนาคต ไม่ทำให้กรณีทดสอบล้มเหลว

## การคืนข้อมูลทดสอบ

ข้อมูล API test อยู่ใน SQLite in-memory เท่านั้น fixture ปิด session, rollback transaction, ปิด connection และ dispose engine หลังจบแต่ละชุดทดสอบ จึงไม่ต้องลบข้อมูลจาก SQL Server หรือฐานข้อมูลโครงการ

## ข้อจำกัด

ยังไม่ได้ทดสอบกับ SQL Server จริง เนื่องจาก environment นี้ไม่มีการตั้งค่า connection สำหรับฐานข้อมูลทดสอบ การทำงานกับ SQL Server ต้องยืนยันเพิ่มเติมใน environment ที่มี config และสิทธิ์เชื่อมต่อของทีม
