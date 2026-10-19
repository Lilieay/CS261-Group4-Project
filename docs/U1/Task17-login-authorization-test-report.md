# Task17: U1 — รายงานทดสอบการป้องกัน Login กับฟังก์ชัน Sprint 1

รายงานนี้ตรวจว่า Login และ Bearer token ป้องกันหน้า/API ของ Sprint 1 ได้จริง ผล Automated Test ไม่ถือเป็นผล Browser UAT หรือผลตรวจรับจาก PO

## 1. ข้อมูลการทดสอบ

| รายการ | รายละเอียด |
|---|---|
| ผู้ทดสอบ | รอระบุผู้ที่ลงมือทดสอบจริง |
| PO/ผู้ตรวจรับ | จะโอ๋ |
| วันที่ทดสอบ | 19 ตุลาคม 2026 |
| รุ่นโค้ด | `49670bb69e7562d1bc1c52423c6ec5a5698efb95` |
| บัญชีทดสอบ | นักศึกษา mock; ไม่บันทึก password/token จริง |
| TU API | Automated Test ใช้ mock; TU API จริงรอทดสอบ |

## 2. ขอบเขตที่ตรวจ

| ส่วน | หน้า/API | กติกา Login |
|---|---|---|
| Auth | `/api/auth/login`, `/status`, `/me`, `/logout` และ `login.html` | Login รับบัญชี; `/me`/logout ต้องใช้ token |
| Course | `courses.html`, `choose-courses.html`, `GET /courses*` | ต้องมี Bearer token |
| Guides | `read-courses.html`, `upload.html`, `GET/POST /guides*` | ต้องมี Bearer token |
| My Guides | `shared-courses.html`, `GET/PUT/DELETE /api/my-guides*` | ต้อง Login และแก้/ลบได้เฉพาะเจ้าของ |
| Preview pages | `index.html`, `saved-courses.html` | การเปิด HTML ไม่ถือว่าได้รับสิทธิ์ API; Backend ต้องตรวจเอง |

## 3. กรณีทดสอบและผล

| รหัส | ข้อมูลที่ใช้ | ผลคาดหวัง | ผลจริง/สถานะ | หลักฐาน |
|---|---|---|---|---|
| T17-01 | บัญชีนักศึกษาและ password ถูกต้อง | HTTP 200, ได้ token และ role=student | ผ่าน | `test_login_success_and_status` |
| T17-02 | password ผิด | HTTP 401, ไม่มี token และไม่สร้าง user | ผ่าน | `test_login_rejects_wrong_password` |
| T17-03 | Login ซ้ำด้วยบัญชีเดิม | ได้ token ใหม่ แต่ใช้ user เดิม ไม่สร้างซ้ำ | ผ่าน | `test_repeated_login_reuses_database_user` |
| T17-04 | ไม่มี token หรือ `Bearer invalid-token` | API ที่ป้องกันตอบ HTTP 401 | ผ่าน | `current_user`, Course/Guide API tests |
| T17-05 | เรียก `/status`, `/me`, logout และใช้ token เดิมหลัง logout | status ถูกต้อง; หลัง logout `/me` ต้องได้ 401 | ผ่าน | `test_logout_invalidates_token` |
| T17-06 | TU ตอบ false/employee/ข้อมูลไม่ครบ หรือ network/config ผิด | ปฏิเสธและไม่สร้าง session/user | ผ่าน 9 subtests | `test_real_tu_refusal_returns_401_without_persisting_user` |
| T17-07 | Database บันทึก user ไม่ได้ | HTTP 503 และไม่มี token | ผ่าน | `test_database_failure_does_not_issue_login_token` |
| T17-08 | My Guides ด้วย token ของตนเอง/ผู้อื่น | เห็นเฉพาะของตนเอง; ผู้ไม่ใช่เจ้าของแก้/ลบไม่ได้ | ผ่าน | My Guides API tests |
| T17-09 | Frontend มี token/ไม่มี token/ได้ 401 | ส่ง Bearer token หรือ redirect ไป Login ตามกรณี | ผ่าน 13 tests | `server.test.js`, `course-api.test.js`, `course-pages.test.js` |
| T17-10 | เปิดหน้าโดยตรงโดยไม่มี Login | หน้า HTML อาจเปิดได้ แต่ API ต้องปฏิเสธเอง | ผ่านตาม route protection; Browser UAT รอทดสอบ | รายการ route ในหัวข้อ 2 |

## 4. ผล Automated Test

Backend รันจาก `backend` ด้วย SQLite ชั่วคราวและ mock TU:

```text
60 passed, 1 warning, 23 subtests passed
```

Frontend รันด้วย Node test runner:

```text
13 passed, 0 failed
```

คำเตือนเป็น deprecation warning ของ Starlette ไม่ใช่ test failure

## 5. ทดสอบ TU API จริง

ให้ผู้ทดสอบตั้งค่าใน `backend/.env` หรือ Environment ที่ไม่ถูก commit:

```text
TU_API_MODE=real
TU_API_URL=<Authentication endpoint ที่ TU อนุญาต>
TU_API_KEY=<Application-Key จาก TU>
TU_API_TIMEOUT=5
TU_TEST_USERNAME=<บัญชีทดสอบที่ได้รับอนุญาต>
TU_TEST_PASSWORD=<รหัสผ่านบัญชีทดสอบ>
```

กรณีที่ต้องทดสอบ:

| รหัส | กรณี | ผลคาดหวัง | ผลจริง/สถานะ |
|---|---|---|---|
| REAL-01 | นักศึกษาทดสอบและข้อมูลถูกต้อง | Login ผ่านและสร้าง token | รอทดสอบจริง |
| REAL-02 | password ผิด | HTTP 401 และไม่สร้าง session | รอทดสอบจริง |
| REAL-03 | บัญชีไม่ใช่นักศึกษา/response ไม่ครบ | ปฏิเสธและไม่ออก token | รอทดสอบจริง |
| REAL-04 | TU API ล่มหรือ timeout | fail-closed และไม่แสดง secret | รอทดสอบจริง |
| REAL-05 | URL/Key ไม่ครบ | Login ไม่สำเร็จและไม่ออก token | รอทดสอบจริง |

ห้ามใส่ password, token, Application-Key หรือ response ที่มีข้อมูลส่วนบุคคลในรายงาน/ภาพหลักฐาน/GitHub

## 6. สถานะ UAT และการตรวจรับ

| รายการ | สถานะ |
|---|---|
| Browser UAT | รอผู้ทดสอบดำเนินการ |
| TU API จริง | รอผู้ทดสอบดำเนินการ |
| หลักฐาน | รอแนบหลังปิดข้อมูลลับ |
| PO ตรวจรับ | รอตรวจ |
| ผลสรุป | ยังไม่สรุปว่า Task17 ผ่านสมบูรณ์ |

เมื่อทดสอบจริงแล้ว ให้เติมผลจริง, ผ่าน/ไม่ผ่าน, หลักฐาน และให้ PO ลงผล `รับรอง` หรือ `ไม่รับรอง` รายงานนี้จึงจะครบถ้วนสำหรับปิดงาน
