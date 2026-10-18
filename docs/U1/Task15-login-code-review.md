# Task15: U1 — Code Review โค้ดการเข้าสู่ระบบ

เอกสารนี้บันทึกผลการตรวจโค้ดการเข้าสู่ระบบหลังงาน Task14 โดยแยกข้อพบที่แก้แล้วออกจากข้อจำกัดที่ยังต้องวางแผนต่อ ไม่ใช้แทนผลทดสอบระบบจริงหรือการตรวจรับ UAT

## 1. ข้อมูลการ Review

| รายการ | รายละเอียด |
|---|---|
| ผู้ตรวจ | ______________________________ |
| วันที่ตรวจ | 19 ตุลาคม 2026 |
| PR ที่ตรวจ | [PR #78 — Task14: รองรับ TU API จริงในการเข้าสู่ระบบ](https://github.com/Lilieay/CS261-Group4-Project/pull/78) |
| Commit ที่ตรวจใน PR | `88892a298515815fa469348f6b409b49601f55f8` |
| Branch ฐาน | `integration/sprint1` |
| โค้ดรุ่นหลัง Review | commit เดียวกับรุ่นที่ตรวจ เนื่องจากไม่พบข้อผิดพลาดระดับต้องแก้ก่อนใช้งาน |
| ขอบเขต | Backend Login, TU verification adapter, session/token และ Frontend Login |

## 2. สิ่งที่ตรวจ

- การตรวจ username และ password ก่อนส่งคำขอ
- การส่งข้อมูลจากหน้า Login ไปยัง Backend
- การเรียก TU Authentication API ในโหมดจริง
- การตรวจว่าเป็นบัญชีนักศึกษาและ response มีข้อมูลจำเป็น
- การสร้างและตรวจ Bearer token
- การออกจากระบบและทำให้ token เดิมใช้ไม่ได้
- การปฏิเสธ token ไม่มีค่า/ผิดรูปแบบ/ไม่ถูกต้อง
- การไม่เก็บ password หรือค่า secret ใน source code และ browser storage
- การจัดการกรณี TU API ล่ม ตอบผิดรูปแบบ หรือ configuration ไม่ครบ
- การแสดง error แบบทั่วไปโดยไม่เปิดเผยรายละเอียดภายใน

## 3. ผลการตรวจโค้ด

| รหัส | จุดที่ตรวจ | ผลตรวจ | ระดับ | การแก้/การตัดสินใจ |
|---|---|---|---|---|
| CR-15-01 | Frontend ตรวจ username เป็นตัวเลขและตรวจ password ว่างก่อนเรียก API | ทำงานตามเงื่อนไข | ผ่าน | ไม่ต้องแก้ |
| CR-15-02 | Frontend ไม่เก็บ password และเก็บเฉพาะ access token ใน session storage | ไม่พบการเก็บ password หรือ request body | ผ่าน | ไม่ต้องแก้ |
| CR-15-03 | Backend ตรวจ `Bearer` token ก่อนให้เรียก `/me` และ `/logout` | ไม่มี token/รูปแบบผิด/token ไม่รู้จัก ได้ HTTP 401 | ผ่าน | ไม่ต้องแก้ |
| CR-15-04 | Login สำเร็จต้องได้รับ token และ user ที่เป็น student | ตรวจ response และ role ก่อนใช้งาน | ผ่าน | ไม่ต้องแก้ |
| CR-15-05 | TU API ตอบไม่ผ่าน, ข้อมูลไม่ครบ, network error หรือ config ไม่ครบ | ระบบ fail-closed และไม่สร้าง session | ผ่าน | ไม่ต้องแก้ |
| CR-15-06 | การส่ง secret ไป TU API | ส่งผ่าน request และ Application-Key จาก environment ไม่ฝังใน source | ผ่าน | ไม่ต้องแก้ |
| CR-15-07 | อายุของ session | session เก็บในหน่วยความจำและไม่มี TTL; token หายเมื่อ process restart แต่ยังไม่หมดอายุเองระหว่าง process ทำงาน | ข้อจำกัดระดับ Medium | ยังไม่แก้ในรอบนี้ เพราะรุ่นปัจจุบันเป็น demo/in-memory; เสนอเพิ่ม TTL หรือ server-side session store ก่อน Production |
| CR-15-08 | การใช้ TU API จริง | automated tests ใช้ mock response ไม่เรียก TU API หรือบัญชีจริง | ขอบเขตหลักฐาน | ระบุข้อจำกัดนี้ในรายงาน ไม่อ้างว่า Production Login ผ่านแล้ว |

## 4. จุดแข็งที่พบ

- รหัสผ่านไม่ถูกเก็บไว้ใน `User` หรือ session object
- ใช้ `secrets.token_urlsafe(32)` สร้าง token แบบสุ่ม
- ใช้ `secrets.compare_digest` ใน mock verification
- ตรวจเฉพาะบัญชีที่มี `type=student` และ `status=true`
- เมื่อ TU API ใช้งานไม่ได้ ระบบไม่สร้าง session แทนที่จะอนุญาตผ่าน
- Frontend แสดงข้อความผิดพลาดทั่วไป ไม่แสดง response ดิบหรือรายละเอียด secret
- Logout ลบ token ออกจาก active session และ token เดิมใช้เรียก `/me` ไม่ได้

## 5. ผลการทดสอบซ้ำหลัง Review

### 5.1 ผลที่รันในรอบ Review นี้

| รายการ | คำสั่ง | ผลจริง | สถานะ |
|---|---|---|---|
| TU API adapter | `backend/.venv/Scripts/python.exe -m pytest -q test/test_tu_api_real.py` | `7 passed, 24 subtests passed` | ผ่าน |
| JavaScript syntax | `node --check frontend/public/js/login.js` | ไม่มี syntax error | ผ่าน |
| Git whitespace | `git diff --check` | ไม่พบ whitespace error | ผ่าน |

### 5.2 ผลที่มีบันทึกไว้จาก PR เดิม

- `test/test_auth.py` ครอบคลุม Login สำเร็จ, password ผิด, status และ logout
- `test/test_tu_api_real.py` ครอบคลุม request contract, response parsing, configuration และ network failure โดยใช้ response จำลอง
- รายงาน Task14 ระบุผลรวมของชุดทดสอบก่อนหน้าไว้แล้ว แต่ผลนั้นไม่ใช่การทดสอบ TU API จริงหรือการทดสอบผ่าน Browser

## 6. ข้อจำกัดและงานที่ต้องทำต่อ

1. การทดสอบนี้ยังไม่ยืนยันว่าบัญชีจริงและ endpoint จริงของ TU ใช้งานได้ เพราะไม่ควรใส่ secret จริงใน Git และ automated tests ใช้ mock
2. session ปัจจุบันเป็น in-memory จึงไม่เหมาะกับการ deploy หลาย instance หรือการเก็บ session ระยะยาว
3. ควรเพิ่ม TTL/วิธี revoke token และ server-side session store ก่อนนำไปใช้งาน Production
4. ควรทดสอบผ่าน Browser และ environment ที่ใช้ deployจริงเพิ่มเติม โดยปกปิด password, token และ response ที่เป็นข้อมูลส่วนบุคคล

## 7. สรุปผล Review

- ผลการ Review: `ผ่านสำหรับรุ่น Demo/Development`
- ข้อบกพร่องที่ต้องแก้ก่อนใช้งานรุ่นนี้: `ไม่พบ`
- ข้อจำกัดที่ต้องแก้ก่อน Production: `session ไม่มี TTL และยังเป็น in-memory`
- โค้ดรุ่นที่อ้างอิง: `88892a298515815fa469348f6b409b49601f55f8`
- ผู้ตรวจยืนยัน: ______________________________ วันที่: ______________
