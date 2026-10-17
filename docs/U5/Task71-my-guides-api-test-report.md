# Task71: U5 — API รายการแนวข้อสอบของฉัน

## API และ DTO

- `GET /api/my-guides` แสดงแนวข้อสอบของผู้ใช้ที่ส่ง Bearer token ถูกต้อง
- ใช้ `current_user` dependency เดิมจาก `app.routers.auth` ในการตรวจสอบ token
- API นำ username จาก Login ไปค้นหา publisher ในฐานข้อมูล จากนั้นกรองรายการด้วยความสัมพันธ์ `guides.publisher_id`; จึงไม่พึ่งพา numeric ID ของผู้ใช้ in-memory ซึ่งอาจไม่ตรงกับ ID ในฐานข้อมูล
- DTO คืน ID, วิชา, ปี/ภาคเรียน, ช่วงสอบ, หัวข้อ, รูปแบบ, จำนวนข้อ, ผู้สอน และคำแนะนำเพิ่มเติม โดยไม่ส่งข้อมูล Login หรือ token กลับมา
- ผู้ใช้ที่ยืนยันตัวตนแล้วแต่ไม่มีรายการจะได้รับ HTTP 200 พร้อม `[]`

## Postman Collection

ไฟล์ `backend/postman/Task71-my-guides.postman_collection.json` มีคำขอ Login และ List my guides. Collection ใช้ตัวแปรว่าง `username`, `password`, `accessToken`; ไม่มี password หรือ token จริงฝังอยู่ ให้กำหนด username/password ใน Postman environment ส่วนตัว แล้วรัน Login ก่อน List my guides. Token ที่ตอบกลับจะถูกเก็บใน collection variable ระหว่างทดสอบ

## ข้อมูลทดสอบและการคืนข้อมูล

API tests ใช้ SQLite in-memory และข้อมูลชั่วคราว: ผู้ใช้ `student`, ผู้ใช้อื่น, ผู้ใช้ `admin`, วิชา CS261 และแนวข้อสอบของ student สองรายการกับของผู้ใช้อื่นหนึ่งรายการ ไม่มีการเชื่อมต่อหรือเปลี่ยนข้อมูล SQL Server จริง ข้อมูลทดสอบถูกลบพร้อมฐานข้อมูล in-memory เมื่อจบแต่ละ test; dependency override และ in-memory sessions ถูกล้างใน teardown

## กรณีทดสอบและผล

| รหัส | ข้อมูลทดสอบ/คำขอ | ผลคาดหวัง | ผลจริง | ผ่าน/ไม่ผ่าน | หลักฐาน |
|---|---|---|---|---|---|
| T71-API01 | Login เป็น student; student มีสองรายการ และผู้ใช้อื่นมีหนึ่งรายการ | HTTP 200; คืนสองรายการของ student เท่านั้น พร้อมฟิลด์ DTO ที่กำหนด | HTTP 200; ได้สองรายการของ student, ไม่พบรายการของผู้ใช้อื่น, ฟิลด์ DTO ครบ | ผ่าน | `test_lists_only_authenticated_users_guides_and_expected_fields` |
| T71-API02 | เรียก `GET /api/my-guides` โดยไม่มี Authorization | HTTP 401 และข้อความขอ Bearer token | HTTP 401; ข้อความตรงตามที่กำหนด | ผ่าน | `test_requires_login_token` |
| T71-API03 | เรียกด้วย `Bearer invalid-token` | HTTP 401 และข้อความ token ไม่ถูกต้อง/หมดอายุ | HTTP 401; ข้อความตรงตามที่กำหนด | ผ่าน | `test_rejects_invalid_login_token` |
| T71-API04 | Login เป็น admin ที่ไม่มี user row/แนวข้อสอบในชุดข้อมูล | HTTP 200 และ JSON array ว่าง `[]` | HTTP 200; ได้ `[]` | ผ่าน | `test_returns_empty_list_when_authenticated_user_has_no_guides` |

## วิธีรันทดสอบ

จากโฟลเดอร์ `backend` (ต้องมี dependencies จาก `requirements.txt` และตั้ง `DB_CONNECTION_STRING` หรือไฟล์ `.env` สำหรับการ import แอป แม้ test จะ override database session ด้วย SQLite):

```powershell
$env:PYTHONPATH='.'
pytest -q test/test_my_guides_api.py
```

## บันทึกผล

```text
pytest: 4 passed, 1 warning in 0.62s (0.62s)
```

คำเตือนที่พบเป็น deprecation warning จาก `starlette.testclient` แนะนำให้ใช้แพ็กเกจ `httpx2`; ไม่มี test ใดล้มเหลว
