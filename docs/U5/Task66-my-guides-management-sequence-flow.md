# Task66: คำอธิบายลำดับ Sequence Diagram — U5

ไฟล์นี้อธิบายผลสำเร็จและกรณีผิดพลาดของรายการ แก้ไข และลบแนวข้อสอบของเจ้าของ ประกอบกับ [แผนภาพ Sequence Diagram](Task66-my-guides-management-sequence-diagram.md)

## ตัวตนและสิทธิ์เจ้าของ

1. UI ส่ง Bearer token ที่ได้จาก Login เดิมไปกับทุกคำขอจัดการ
2. API เรียก `current_user(credentials)` ก่อนทำงาน ถ้าไม่มี token, token ไม่ถูกต้อง หรือถูกยกเลิกแล้ว ให้ตอบ `401 AUTH_REQUIRED` และไม่เรียก DAO ที่อ่าน/แก้/ลบแนวข้อสอบ
3. `current_user` คืน username ที่ผ่านการยืนยันตัวตนแล้ว API ใช้ `UserDAO.get_by_username(username)` ซึ่งเป็น DAO เดิมเพื่ออ่าน `users.id` ในฐานข้อมูล
4. DAO ที่อ่าน/แก้/ลบต้องจำกัดผลด้วยเจ้าของจากฐานข้อมูลเสมอ ไม่เชื่อ ID ที่ UI ส่งมาเป็นตัวระบุเจ้าของ และไม่อาศัยการซ่อนปุ่มบน UI
5. ไม่พบแถวหรือผู้ใช้ไม่ใช่เจ้าของให้ใช้ `404 GUIDE_NOT_FOUND` เพื่อไม่เปิดเผยว่ารายการของผู้อื่นมีอยู่หรือไม่

## ดูรายการ

1. ผู้ใช้เปิดหน้าแนวข้อสอบของฉัน แล้ว UI เรียก `GET /api/my-guides`
2. หลัง `current_user` ผ่าน API เรียก `MyGuideDAO.list_by_username(username)`
3. DAO join `guides` กับ `users` แล้วเลือกเฉพาะ username ของผู้ใช้ พร้อมโหลด Course สำหรับข้อมูลใน `MyGuideDTO`
4. ถ้าพบข้อมูล ตอบ `200` พร้อมรายการของเจ้าของเท่านั้น; ถ้าไม่พบรายการ ตอบ `200 []`
5. ถ้าเกิดข้อผิดพลาดระหว่างอ่าน ให้ตอบ `500 INTERNAL_ERROR` และ UI แจ้งโหลดไม่สำเร็จโดยไม่แสดงข้อมูลปลอมว่าโหลดสำเร็จ

## แก้ไข

1. UI เติมฟอร์มจากรายการที่ผู้ใช้เลือก ผู้ใช้แก้ฟิลด์ Guide แล้วกดบันทึก
2. UI เรียก `PUT /api/my-guides/{guide_id}` พร้อมข้อมูลแก้ไขและ Bearer token
3. API ตรวจ payload ตามกติกา U5; ถ้าไม่ผ่านตอบ `422 VALIDATION_ERROR` และไม่เรียกเมธอดแก้ไข
4. API map username ไปยัง `users.id` แล้วเรียกเมธอดที่เสนอ `UpdateOwnedGuideDAO.update_owned(guide_id, publisher_id, payload)`
5. DAO ทำ `UPDATE` โดยมีทั้ง `guides.id` และ `guides.publisher_id` ในเงื่อนไขเดียวกัน
6. เมื่อแก้ไขได้หนึ่งแถว API commit และตอบ `200 MyGuideDTO`; UI ปรับข้อมูลที่แสดงเป็นค่าล่าสุด
7. ถ้าไม่พบรายการหรือเจ้าของไม่ตรง ตอบ `404 GUIDE_NOT_FOUND`; ถ้าฐานข้อมูล/commit ล้มเหลว rollback, ตอบ `500 INTERNAL_ERROR` และรักษาข้อมูลเดิม

## ลบ

1. UI ขอคำยืนยันก่อน หากผู้ใช้ยกเลิก ให้ปิดกล่องยืนยันโดยไม่เรียก API
2. เมื่อยืนยัน UI เรียก `DELETE /api/my-guides/{guide_id}` พร้อม Bearer token
3. API ตรวจ Login และ map username เป็น `users.id` แล้วเรียก `DeleteOwnedGuideDAO.delete_owned(guide_id, publisher_id)`
4. DAO ลบด้วยเงื่อนไขทั้ง `guides.id` และ `guides.publisher_id`; DAO ไม่ลบแถวอื่นหรือ Course/User
5. เมื่อ DAO คืน `True` API commit และตอบ `204 No Content`; UI นำรายการออกและแจ้งลบสำเร็จ
6. ถ้า DAO คืน `False` เพราะไม่พบรายการหรือเจ้าของไม่ตรง ให้ตอบ `404 GUIDE_NOT_FOUND`; ถ้าฐานข้อมูล/commit ล้มเหลว rollback และตอบ `500 INTERNAL_ERROR`

## เมธอดและหน้าที่

| ชั้น | เมธอด/ฟังก์ชัน | หน้าที่ |
|---|---|---|
| UI | `loadMyGuides()` (ชื่ออ้างอิงใน design) | เรียก API รายการและแสดง state ว่าง/ผิดพลาด |
| UI | `submitGuideEdit()` (ชื่ออ้างอิงใน design) | ส่งฟอร์มแก้ไขหลัง validation |
| UI | `confirmGuideDelete()` (ชื่ออ้างอิงใน design) | ส่ง DELETE หลังผู้ใช้ยืนยันเท่านั้น |
| API/Auth | `current_user(credentials)` | ตรวจ Bearer token และคืนผู้ใช้ที่ Login แล้ว |
| DAO เดิม | `UserDAO.get_by_username(username)` | map username ไป `users.id` |
| DAO รายการ | `MyGuideDAO.list_by_username(username)` | อ่านรายการที่เป็นของ username นั้น |
| DAO แก้ไข | `UpdateOwnedGuideDAO.update_owned(guide_id, publisher_id, payload)` | contract ที่เสนอ; ต้อง update เฉพาะรายการเจ้าของ |
| DAO ลบ | `DeleteOwnedGuideDAO.delete_owned(guide_id, publisher_id)` | ลบเฉพาะรายการเจ้าของและคืนสถานะว่าลบได้หรือไม่ |

ชื่อฟังก์ชัน UI สำหรับการออกแบบไม่ได้อ้างว่าเป็นชื่อ JavaScript ที่มีอยู่ใน branch ปัจจุบัน ส่วน `UpdateOwnedGuideDAO.update_owned` เป็นชื่อที่เสนอสำหรับงาน implementation ในอนาคต; Task66 ไม่ได้เพิ่มโค้ดหรือ DAO

## ขอบเขต Entity/ER

ใช้ `Guide`, `User` และ `Course` ตาม ER เดิมใน docs/U1 และ docs/U3 เท่านั้น ไม่มี Entity, ตาราง หรือฟิลด์ใหม่ใน Task66
