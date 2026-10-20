# Task11: U1 — เขียนส่วนยืนยันบัญชีกับ TU API

## หน้าที่ของ adapter

- `backend/app/services/tu_api.py` เป็น Adapter สำหรับยืนยันบัญชีกับ TU API
- `backend/app/services/auth.py` เรียก Adapter ก่อนสร้าง session และอนุญาตเฉพาะ `account_type=student` กับ `active=true`
- หาก TU API ล่ม, ตั้งค่าไม่ครบ, ตอบข้อมูลไม่ครบ หรือประเภทบัญชีไม่ใช่นักศึกษา ระบบจะไม่สร้าง session (fail-closed)
- ไม่เก็บรหัสผ่านไว้ใน `User` หรือข้อมูลโปรไฟล์

## Contract ของ TU API จริง

ตั้งค่าใน environment ของ Backend:

```text
TU_API_MODE=real
TU_API_URL=<TU Authentication API endpoint>
TU_API_KEY=<Application-Key จาก TU API Developer>
TU_API_TIMEOUT=5
```

สำหรับ Compose ให้ตั้งค่าใน `.env` ที่ root ของ repository โดย `compose.yaml` ส่งต่อทั้งสี่ค่าให้ Backend ค่าเริ่มต้นคือ `mock`, URL/key ว่าง และ timeout 5 วินาที. เมื่อติดตั้ง Backend โดยตรง `backend/app/config.py` โหลด `backend/.env` ก่อนเริ่มแอป โดยค่าจาก process environment มีลำดับความสำคัญสูงกว่า. การทดสอบ adapter โดยตรงอ่านค่าจาก `os.environ`.

Request ที่ส่งไปยัง TU API:

```json
{"UserName":"<บัญชีทดสอบ>","PassWord":"<ส่งผ่าน request เท่านั้น>"}
```

Adapter ส่ง Header Application-Key และอ่าน status, type, displayname_th และ displayname_en ยอมรับเมื่อ status เป็น true, type เป็น student และมีชื่อไม่ว่างอย่างน้อยหนึ่งภาษา โดยเลือกชื่อไทยก่อนชื่ออังกฤษมาเป็น TUAccount.display_name

Adapter ไม่ได้อ่านฟิลด์ active จาก response แต่กำหนด TUAccount.active=True หลังผ่านเงื่อนไขข้างต้น ค่านี้เป็นกติกาภายใน ไม่ได้ยืนยันสถานะการลงทะเบียนเรียนเพิ่มเติม AuthService ปัจจุบันส่ง display_name นี้เข้าพารามิเตอร์ displayname_en ของ UserDAO ไม่ได้บันทึกชื่อสองภาษาแยกคอลัมน์ครบทุกครั้ง

ไม่บันทึก request password หรือ response ที่มีข้อมูลลับลงใน log/report

## โหมดจำลองสำหรับการทดสอบ

หากไม่ตั้งค่า `TU_API_MODE` ระบบใช้ `mock` เพื่อให้โปรเจกต์สาธิตทำงานได้ โดยบัญชีเริ่มต้น `6800000000 / 0000000000000` เป็นข้อมูลจำลองเท่านั้น และปรับได้ด้วย `TU_MOCK_USERNAME` กับ `TU_MOCK_PASSWORD`. บัญชี `admin / admin123` ถูกกำหนดเป็น `staff` และต้องถูกปฏิเสธ ไม่ใช่ผลจาก TU API จริง

## พฤติกรรมที่ตรวจจากโค้ด

| กรณี | ข้อมูลทดสอบ | ผลที่คาดหวัง | ผลจริงจากโค้ด | สถานะ |
|---|---|---|---|---|
| นักศึกษา TU ผ่าน | `6800000000 / 0000000000000` ใน mock mode | ยืนยันสำเร็จและสร้าง session | บัญชี mock ผ่านเงื่อนไขนักศึกษา | IMPLEMENTED |
| รหัสผ่านไม่ถูกต้อง | `6800000000 / wrong` | ไม่สร้าง session, HTTP 401 | Adapter คืน `None` และ Login ปฏิเสธ | IMPLEMENTED |
| อาจารย์/บุคลากร | `admin / admin123` ใน mock mode | ต้องปฏิเสธ | `account_type=staff` ไม่ผ่าน | IMPLEMENTED |
| TU API ไม่พร้อม | real mode, URL เรียกไม่ได้ | fail-closed, ไม่สร้าง session | `TUVerificationError` ถูกปฏิเสธ | IMPLEMENTED |
| Response ยืนยันไม่ครบ | real mode, ขาด status/type/name หรือชนิดข้อมูลไม่ถูกต้อง | ไม่อนุญาต | Adapter คืน `None` | IMPLEMENTED |
| ไม่ส่งบัญชีว่าง | username เป็นช่องว่าง | ไม่เรียก TU API | AuthService.login trim แล้ว raise LoginRejected ก่อนเรียก adapter | IMPLEMENTED |

## ขอบเขตหลักฐาน

ตารางข้างต้นเป็นการอธิบายเส้นทางในโค้ด ไม่ใช่ผล UAT ผล automated tests และ revision ที่รันจริงดู [รายงาน Task14](../testing/task14-login-ui-api-test-report.md#การตรวจสอบ)

การทดสอบอัตโนมัติในรายงานใช้ HTTP response จำลอง ไม่ใช้แทนผลยืนยัน TU จริงของเครื่องที่นำไปสาธิต ผลตรวจรับ TU จริงต้องบันทึกรุ่นระบบ วันทดสอบ และหลักฐานของรอบนั้น โดยไม่ใส่รหัสผ่านหรือ API key

ดู [โค้ด adapter](../../../backend/app/services/tu_api.py), [AuthService](../../../backend/app/services/auth.py) และ [Login API contract](task5-login-api-spec.md)
