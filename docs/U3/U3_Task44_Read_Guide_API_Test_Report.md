# Task44: รายงานทดสอบ API อ่านแนวข้อสอบ

## ขอบเขต

ทดสอบ API รายการ ตัวกรอง รายละเอียด และตัวเลือกกรอง โดยส่ง Bearer token จากระบบ Login เดิม ใช้ฐาน SQLite ชั่วคราวพร้อมข้อมูลจำลองใน test fixture; ไม่ใช้ข้อมูลจริงในฐานข้อมูล

## ผลทดสอบ

คำสั่งจากโฟลเดอร์ `backend`:

```powershell
.venv\Scripts\python.exe -m unittest discover -s test -p test_read_guide_api.py -v
```

ผลจริง: **8 API tests passed** (TestClient, SQLite) และ **3 Auth regression cases passed**

| รหัส | ข้อมูลทดสอบ | ผลคาดหวัง | ผลจริง | สถานะ | หลักฐาน |
|---|---|---|---|---|---|
| T44-API-01 | ไม่มี Bearer token เรียกรายการ | 401 `AUTH_REQUIRED` | 401 พร้อม error code ตามกำหนด | ผ่าน | `test_list_requires_login_and_returns_only_requested_course` |
| T44-API-02 | Login แล้วอ่าน CS261 | 200, มีเฉพาะรายการของ CS261 พร้อม publisher | 200, คืน 2 รายการของ CS261 | ผ่าน | `test_list_requires_login_and_returns_only_requested_course` |
| T44-API-03 | ปี 2568, ภาค 1, กลางภาค | คืนรายการที่ตรงทุกเงื่อนไข | คืน “กลางภาค 2568” รายการเดียว | ผ่าน | `test_list_applies_combined_filters_and_distinguishes_no_match` |
| T44-API-04 | ปี 2500 ในวิชาที่มีรายการ | 200, `has_guides=true`, `items=[]` | ตรงตามคาด | ผ่าน | `test_list_applies_combined_filters_and_distinguishes_no_match` |
| T44-API-05 | ภาค 4, ปีไม่ใช่ตัวเลข, query `instructor` | 422 `INVALID_PARAMETERS` | ทั้งสามกรณีตอบ 422 ตามรูปแบบ error | ผ่าน | `test_list_rejects_invalid_and_unknown_filters` |
| T44-API-06 | course_id 999 | 404 `COURSE_NOT_FOUND` | ตรงตามคาด | ผ่าน | `test_list_returns_course_not_found` |
| T44-API-07 | อ่านรายละเอียดรายการ 1 ที่มีข้อมูลเสริมเป็น null | 200, เนื้อหา/วิชา/ค่า null ครบ | ข้อความหลายบรรทัดและ instructor/count/advice ที่ว่างถูกส่งเป็น null | ผ่าน | `test_detail_returns_complete_data_with_nullable_fields` |
| T44-API-08 | guide_id 999 | 404 `GUIDE_NOT_FOUND` | ตรงตามคาด | ผ่าน | `test_detail_missing_guide_returns_expected_error` |
| T44-API-09 | ตัวเลือกของวิชาที่มีและไม่มีรายการ | ค่าซ้ำถูกตัดและเรียง; วิชาว่างได้ array ว่าง | ปี `[2567, 2568]`, ช่วงสอบ `[final, midterm]`; วิชาว่างคืน `[]` | ผ่าน | `test_filter_options_are_unique_scoped_and_empty_when_no_guides` และ `test_list_for_course_without_guides_returns_empty_state` |
| T44-API-10 | Login สำเร็จ, password ผิด, Logout แล้วใช้ token เดิม | พฤติกรรม Login เดิมยังครบ | ผ่านทั้ง 3 กรณี | ผ่าน | `backend/test/test_auth.py` เรียกฟังก์ชันทดสอบเดิมโดยตรง |

## Postman

Collection: [U3_Task44_Read_Guide_API.postman_collection.json](U3_Task44_Read_Guide_API.postman_collection.json)

ตั้งค่า `base_url`, `username`, `password`, `course_id`, `guide_id` และตัวแปร filter ใน Postman Environment ก่อนรัน Login และ request อื่น ๆ Collection เก็บ token ไว้ใน collection variable หลัง Login แต่ไม่มีรหัสผ่านหรือ token จริง

## วิธีรันด้วยข้อมูลฐานข้อมูลจริง

1. ตั้ง `DB_CONNECTION_STRING` ตามค่าใน `backend/.env` และเริ่ม API ด้วย `uvicorn app.main:app --reload`
2. Import Collection แล้วกรอก Environment variables ในเครื่อง
3. เรียก Login เพื่อบันทึก token จากนั้นเรียก API อ่านรายการ รายละเอียด และตัวเลือกกรอง
4. ใช้ course และ guide ID ที่มีอยู่จริงในฐานข้อมูล; ไม่ต้องบันทึกรหัสผ่านหรือ token ลงใน Collection

การทดสอบในรายงานนี้รันผ่าน TestClient กับ SQLite fixture ยังไม่ได้รัน Collection กับ SQL Server จริง
