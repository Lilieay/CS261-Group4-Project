# Task66 U5 คำอธิบายลำดับและขอบเขต

อ่านคู่กับ [Sequence Diagram ปัจจุบัน](task66-my-guides-management-sequence-diagram.md) ไฟล์นี้สรุปเมธอดจริงและ HTTP contract โดยไม่เพิ่ม flow เป้าหมายที่ยังไม่ได้ implement

## การแบ่งหน้าที่

| ชั้น | เมธอดหรือส่วนที่ใช้จริง | หน้าที่ |
|---|---|---|
| Browser | `loadMyGuides()` ใน shared-courses.js | โหลดรายการและแสดง state |
| Browser | `open(row, saved)` และ submit listener ใน edit-form.js | เปิดฟอร์ม ตรวจค่า ส่ง update และเรียก callback โหลดรายการ |
| Browser | click listeners ใน shared-courses.js | ยืนยันหรือยกเลิกลบ ป้องกันส่งซ้ำ และโหลดรายการใหม่ |
| API client | `GuideApi.mine/update/remove` | ส่ง token ตรวจ response และรายงานกรณียืนยันผลไม่ได้ |
| Node | routes ของ `/api/my-guides` | proxy GET/PUT/DELETE ไป backend |
| Auth dependency | `current_user(credentials, auth_service)` | ตรวจ Session และคืน token กับ AuthenticatedUser |
| Service | `MyGuidesService.list_for_user/update/delete` | ประสาน DAO แปลง DTO และควบคุม transaction ของงานเขียน |
| UserDAO | `get_by_username(username)` | map บัญชีที่ Login เป็น User สำหรับตรวจเจ้าของ |
| CourseDAO | `get_by_id(course_id)` | ตรวจรายวิชาปลายทางในงานแก้ไข |
| MyGuideDAO | `list_by_username(username)` | อ่านเฉพาะผลงานของบัญชีนั้น |
| UpdateOwnedGuideDAO | `update_owned(guide_id, publisher_id, payload)` | update ด้วย ID และเจ้าของใน SQL เดียวกัน แล้วอ่านข้อมูลล่าสุด |
| DeleteOwnedGuideDAO | `delete_owned(guide_id, publisher_id)` | delete ด้วย ID และเจ้าของใน SQL เดียวกัน คืน bool |

Service และ DAO ถูกประกอบใน `get_my_guides_service` โดยใช้ Session เดียวกัน Router ไม่สร้าง DAO และไม่ commit เอง

## ผลสำเร็จและข้อผิดพลาด

| การทำงาน | ผลสำเร็จ | ข้อผิดพลาดที่ต้องอธิบาย |
|---|---|---|
| GET `/api/my-guides` | `200 list[MyGuideDTO]` หรือ `[]` | 401 เมื่อ Session ใช้ไม่ได้ ส่วน unhandled storage error เป็น server error |
| PUT `/api/my-guides/{guide_id}` | `200 MyGuideUpdateResponse` | 404 `GUIDE_NOT_FOUND`, 422 `COURSE_NOT_FOUND` หรือ validation, 500 `GUIDE_UPDATE_FAILED` |
| DELETE `/api/my-guides/{guide_id}` | `200 {id, message}` | 404 `GUIDE_NOT_FOUND`, 422 สำหรับ ID ไม่ถูกต้อง, 500 `GUIDE_DELETE_FAILED` |

ข้อผิดพลาด U5 ใช้ `detail` โดย validation ของ Pydantic เป็นรายการรายละเอียด ไม่ใช้ envelope `error.code` แบบ API อ่าน/เผยแพร่ของ U3/U4 Proxy อาจตอบ 502 เมื่อ upstream ใช้ไม่ได้

## สิทธิ์และการเปลี่ยนข้อมูล

รายการกรองผ่าน username ที่ Session ยืนยันแล้ว งานแก้ไขและลบอ่าน `users.id` จาก UserDAO แล้วใช้เป็น `publisher_id` ใน SQL ไม่รับเจ้าของใหม่จาก UI ไม่พบหรือเจ้าของไม่ตรงใช้ 404 เช่นเดียวกัน

การแก้ไขใช้ Guide ID เดิม การเปลี่ยนรายวิชาแก้ FK ไป Course เดิมในระบบ การลบ Guide ไม่ลบ Course หรือ User แต่ `saved_guides` ที่อ้าง Guide นั้นถูกลบตาม FK `ON DELETE CASCADE`

ปีสำหรับแก้ไขรับ 2566–2569 ส่วนรายวิชาปลายทางใน service ปัจจุบันตรวจเพียงมีอยู่ด้วย `get_by_id` อย่าอธิบายว่ามี CS-only guard ในเมธอดนี้แล้ว

Service เรียก commit ก่อน `_to_dto` ในงาน update หาก DTO อ่านข้อมูลจาก DB ไม่สำเร็จหลัง commit อาจตอบ failure ทั้งที่ข้อมูลเปลี่ยนแล้ว การ rollback ใน exception handler ไม่ย้อน commit ที่สำเร็จไปก่อนหน้า ประเด็นนี้เป็นข้อจำกัดโค้ดปัจจุบัน ไม่ได้แก้ในงาน Diagram

## เอกสารและโค้ดที่เกี่ยวข้อง

- [My Guides API spec](task65-my-guides-api-spec.md)
- [MyGuidesService](../../../backend/app/services/my_guides.py)
- [MyGuideUpdateRequest](../../../backend/app/schemas/my_guide_update.py) และ [MyGuideDeleteResponse](../../../backend/app/schemas/my_guide_delete.py)
- [ER และ Entity ของ Guide](../../U3/design/task36-db-er-entity-dao.md), [User](../../U1/design/task6-db-er-entity-dao.md) และ [Course](../../U2/design/task22-course-entity.md)
