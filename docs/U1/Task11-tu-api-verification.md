# Task11: U1 — เขียนส่วนยืนยันบัญชีกับ TU API

## Artifact

- `backend/app/services/tu_api.py` เป็น Adapter สำหรับยืนยันบัญชีกับ TU API
- `backend/app/services/auth.py` เรียก Adapter ก่อนสร้าง session และอนุญาตเฉพาะ `account_type=student` กับ `active=true`
- หาก TU API ล่ม, ตั้งค่าไม่ครบ, ตอบข้อมูลไม่ครบ หรือประเภทบัญชีไม่ใช่นักศึกษา ระบบจะไม่สร้าง session (fail-closed)
- ไม่เก็บรหัสผ่านไว้ใน `User` หรือข้อมูลโปรไฟล์

## Contract ของ TU API จริง

ตั้งค่าใน environment ของ Backend:

```text
TU_API_MODE=real
TU_API_URL=https://<tu-api-host>/verify
TU_API_TIMEOUT=5
```

Request ที่ส่งไปยัง TU API:

```json
{"username":"<บัญชีทดสอบ>","password":"<ส่งผ่าน request เท่านั้น>"}
```

Response ที่ระบบยอมรับต้องยืนยันครบทุกค่า:

```json
{
  "authenticated": true,
  "active": true,
  "account_type": "student",
  "username": "<บัญชีที่ผ่านการยืนยัน>",
  "display_name": "<ชื่อที่แสดง>"
}
```

ไม่บันทึก request password หรือ response ที่มีข้อมูลลับลงใน log/report

## โหมดจำลองสำหรับการทดสอบ

หากไม่ตั้งค่า `TU_API_MODE` ระบบใช้ `mock` เพื่อให้โปรเจกต์สาธิตทำงานได้ โดยบัญชี `student / password123` เป็นข้อมูลจำลองเท่านั้น บัญชี `admin` ถูกกำหนดเป็น `staff` และต้องถูกปฏิเสธ ไม่ใช่ผลจาก TU API จริง

## Test report

| กรณี | ข้อมูลทดสอบ | ผลที่คาดหวัง | ผลจริงจากโค้ด | สถานะ |
|---|---|---|---|---|
| นักศึกษา TU ผ่าน | `student / password123` ใน mock mode | ยืนยันสำเร็จและสร้าง session | `TUAccount(student)` ผ่านเงื่อนไขนักศึกษา | IMPLEMENTED |
| รหัสผ่านไม่ถูกต้อง | `student / wrong` | ไม่สร้าง session, HTTP 401 | Adapter คืน `None` และ Login ปฏิเสธ | IMPLEMENTED |
| อาจารย์/บุคลากร | `admin / admin123` ใน mock mode | ต้องปฏิเสธ | `account_type=staff` ไม่ผ่าน | IMPLEMENTED |
| TU API ไม่พร้อม | real mode, URL เรียกไม่ได้ | fail-closed, ไม่สร้าง session | `TUVerificationError` ถูกปฏิเสธ | IMPLEMENTED |
| Response ยืนยันไม่ครบ | real mode, ขาด `active`/`account_type` | ไม่อนุญาต | ตรวจ explicit proof และคืน `None` | IMPLEMENTED |
| ไม่ส่งบัญชีว่าง | username เป็นช่องว่าง | ไม่เรียก TU API | `authenticate` คืน `None` ก่อนเรียก Adapter | IMPLEMENTED |

## ขอบเขตหลักฐาน

ยังไม่มี TU API endpoint และบัญชีทดสอบจริงใน repository นี้ จึงยังไม่อ้างว่าได้ทดสอบกับ TU API จริง ผล `mock` ใช้ตรวจ flow เท่านั้น เมื่อต่อ endpoint จริงต้องตั้ง `TU_API_MODE=real`, ใช้บัญชีทดสอบที่ได้รับอนุญาต และแนบ response ที่ปกปิดข้อมูลลับในรอบทดสอบจริง

