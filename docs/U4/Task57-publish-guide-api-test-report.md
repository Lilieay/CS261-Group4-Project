# Task57: U4 — API เผยแพร่แนวข้อสอบและตรวจข้อมูลฝั่ง Backend

## ขอบเขตและการทำงาน

เพิ่ม `POST /guides` ใน Guide Router และ `GuidePublishRequestDTO` สำหรับตรวจข้อมูลก่อนบันทึก โดยใช้ `current_user` ตัวเดิมจาก Login และไม่รับ `publisher_id` จาก Request

Service ตรวจว่ารายวิชามีอยู่และรหัสขึ้นต้นด้วย `CS`, resolve `users.id` จาก username ที่ Login ยืนยันแล้วผ่าน `UserDAO`, สร้าง Entity ด้วย `PublishGuideDAO` ของ Task56 และ commit รายการแนวข้อสอบเมื่อสำเร็จ เมื่อเกิดข้อผิดพลาดระหว่างสร้าง Guide จะ rollback transaction และตอบ `500 INTERNAL_ERROR`

ชื่อและหัวข้อถูก trim และต้องไม่ว่าง, จำนวนข้อที่ระบุต้องเป็น integer มากกว่า 0, ค่าภาคเรียน/ช่วงสอบ/รูปแบบต้องอยู่ในตัวเลือกที่ API อ่านรองรับ และคำแนะนำว่างถูก normalize เป็น `NULL` ปีการศึกษาตรวจตามชุดปัจจุบันใน `frontend/public/js/upload-config.js`: `2566`, `2567`, `2568`, `2569` Request ที่ส่ง field เพิ่ม เช่น `publisher_id` ถูกปฏิเสธ

> ข้อสังเกตเรื่อง Login: `current_user` คืน user จาก in-memory session ส่วน `Guide.publisher_id` อ้างถึงฐานข้อมูล ดังนั้น service ใช้ username ที่ยืนยันแล้วเรียก `UserDAO.get_or_create_from_tu_profile()` เพื่อ resolve `users.id` และชื่อผู้เผยแพร่ตาม Entity U1

## Postman Collection

ไฟล์ `backend/postman/Task57-publish-guide.postman_collection.json` มีคำขอทดสอบ success, ไม่มี token และข้อมูลไม่ถูกต้อง โดยไม่มี password หรือ token จริง ให้ตั้ง collection variables ในเครื่องของผู้ทดสอบ:

| Variable | ค่า |
|---|---|
| `baseUrl` | URL ของ Backend เช่น `http://127.0.0.1:8000` |
| `accessToken` | token ที่ได้จากการ Login ในเครื่อง; อย่า commit ค่าจริงลง collection |
| `courseId` | ID ของวิชา CS ที่มีอยู่ในฐานทดสอบ |

## วิธีรันทดสอบ

จาก `backend`:

```powershell
python -m pytest test/test_publish_guide_api.py -q
```

API tests ใช้ SQLite ชั่วคราวและ FastAPI TestClient โดยสร้าง token ผ่านระบบ session เดิม ไม่เรียก TU API จริงหรือฐานข้อมูล production

## รายงานผล API Test

| รหัส | ข้อมูลทดสอบ | ผลคาดหวัง | ผลจริง | ผ่าน/ไม่ผ่าน | หลักฐาน |
|---|---|---|---|---|---|
| T57-API01 | token ถูกต้อง, วิชา CS261 มีอยู่, payload ครบ | `201`, ได้ Guide ID และรายละเอียด โดย publisher เป็นผู้ Login | ได้ `201`, รายละเอียดครบ และ DB `publisher_id` อ้างถึง User ของ username ใน token | ผ่าน | `test_publish_uses_authenticated_user_and_returns_created_detail` |
| T57-API02 | ไม่มี token และ token ใช้ไม่ได้ | `401 AUTH_REQUIRED`, ไม่บันทึก Guide | ทั้งสองกรณีได้ `401 AUTH_REQUIRED` | ผ่าน | `test_publish_requires_a_valid_login_token` |
| T57-API03 | ไม่ส่ง title, title/topics ว่าง, ปี/semester/period ไม่ถูกต้อง, count เป็น 0/ทศนิยม, count ไม่ตรงรูปแบบ, ส่ง `publisher_id` เพิ่ม | `422 INVALID_PARAMETERS`, ไม่บันทึก Guide | 10 payload ย่อยได้ `422`; จำนวน Guide ยังคงเป็น 0 | ผ่าน | `test_publish_rejects_missing_blank_invalid_and_spoofed_fields` (10 subtests) |
| T57-API04 | course ID ไม่มีอยู่ หรือเป็น MA111 ที่ไม่ใช่วิชา CS | `404 COURSE_NOT_FOUND`, ไม่สร้าง Guide | ทั้งสองกรณีได้ `404 COURSE_NOT_FOUND`; ไม่มี Guide หรือ User ใหม่จากคำขอเหล่านี้ | ผ่าน | `test_publish_rejects_missing_and_out_of_scope_courses` (2 subtests) |
| T57-API05 | payload ถูกต้องโดยไม่ระบุ counts และคำแนะนำเป็นช่องว่าง | `201`, counts และคำแนะนำยังเป็น `NULL` | ได้ `201`; `subjective_count` และ `additional_advice` เป็น `NULL` | ผ่าน | `test_publish_allows_nullable_optional_values_and_normalizes_advice` |
| T57-API06 | จำลอง DAO create ล้มเหลวหลังตรวจข้อมูล | `500 INTERNAL_ERROR`, ไม่มี Guide บางส่วน | ได้ `500 INTERNAL_ERROR`; ไม่พบ Guide ที่สร้างค้างไว้ | ผ่าน | `test_database_failure_returns_500_and_rolls_back_guide` |

**ผลรันจริง:** API Task57 `6 passed, 12 subtests passed` บน SQLite; เมื่อลองร่วมกับ DAO Task56 และ API อ่านเดิมได้ `19 passed, 15 subtests passed` มี Starlette deprecation warning จาก TestClient/httpx ซึ่งไม่ทำให้ test ล้มเหลว ไม่ได้ทดสอบกับ SQL Server ในรายงานนี้
