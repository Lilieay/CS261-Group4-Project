# Task17: U1 — รายงานทดสอบการป้องกัน Login กับฟังก์ชัน Sprint 1

รายงานนี้ตรวจว่าหน้าและ API ใน Sprint 1 บังคับให้ Login ก่อนใช้งานหรือไม่ รวมทั้งตรวจบัญชีที่ใช้ได้ บัญชีที่ไม่ควรผ่าน token ที่ไม่มี/ผิด และกรณีระบบยืนยันตัวตนหรือฐานข้อมูลมีปัญหา ผล Automated Test ในรายงานนี้ไม่ใช่ผลการ Demo ผ่าน Browser จริง เว้นแต่ระบุไว้ชัดเจน

## 1. ข้อมูลการทดสอบ

| รายการ | รายละเอียด |
|---|---|
| ผู้ทดสอบ | ______________________________ |
| PO/ผู้ตรวจรับ | ______________________________ |
| วันที่ทดสอบ | 19 ตุลาคม 2026 |
| รุ่นโค้ดที่ทดสอบ | `49670bb69e7562d1bc1c52423c6ec5a5698efb95` |
| Backend | FastAPI + TestClient, SQLite ชั่วคราว |
| Frontend | Node test runner และ HTTP proxy ในเครื่อง |
| TU API mode | `mock` ใน automated test; ไม่เรียก TU API จริง |
| บัญชีทดสอบที่ใช้ | นักศึกษา mock `6800000000` และรหัสผ่านจำลองที่ไม่บันทึกในรายงาน; กรณีรหัสผ่านผิดใช้ค่า `wrong` |
| ข้อมูลลับ | ไม่บันทึก password, access token หรือ Application-Key จริง |

## 2. ขอบเขตหน้าและ API

### API ที่ต้องตรวจ Login

| กลุ่ม | เส้นทาง | สิทธิ์ที่คาดหวัง |
|---|---|---|
| Authentication | `POST /api/auth/login` | ไม่ต้องมี token แต่ต้องยืนยันบัญชีและ password |
| Authentication | `GET /api/auth/status` | ไม่มี token ได้สถานะ `logged_in=false`; token ถูกต้องได้ข้อมูลผู้ใช้ |
| Authentication | `GET /api/auth/me` | ต้องมี Bearer token ที่ถูกต้อง |
| Authentication | `POST /api/auth/logout` | ต้องมี Bearer token ที่ถูกต้อง |
| Course | `GET /courses`, `GET /courses/{course_id}` | ต้อง Login |
| Read/Publish Guide | `GET /courses/{course_id}/guides`, `GET /guides/{guide_id}`, `GET /courses/{course_id}/guides/filter-options`, `POST /guides` | ต้อง Login |
| My Guides | `GET /api/my-guides` | ต้อง Login และคืนเฉพาะของผู้ใช้ปัจจุบัน |
| My Guides | `PUT /api/my-guides/{guide_id}` | ต้อง Login และต้องเป็นเจ้าของรายการ |
| My Guides | `DELETE /api/my-guides/{guide_id}` | ต้อง Login และต้องเป็นเจ้าของรายการ |

### หน้าที่เกี่ยวข้อง

- `login.html`: รับข้อมูล Login และเก็บเฉพาะ access token ใน `sessionStorage` หลัง Login สำเร็จ
- `courses.html` และ `choose-courses.html`: เรียก Course API พร้อม Bearer token
- `read-courses.html`: ใช้ API อ่านรายละเอียดและรายการแนวข้อสอบ
- `upload.html`: ใช้ API เผยแพร่เมื่อเปิดโหมด API; โหมด preview เป็นข้อมูล localStorage และไม่ใช่การตรวจสิทธิ์ Backend
- `shared-courses.html`: ใช้สำหรับดู/แก้ไข/ลบรายการของฉันตามโหมดที่หน้าเว็บเปิดใช้
- `index.html` และ `saved-courses.html`: หน้าส่วนติดต่อ/ข้อมูล preview บางส่วน จึงต้องแยกจาก API ที่บังคับ Login และไม่ถือว่าการเปิด HTML เพียงอย่างเดียวคือการผ่านสิทธิ์ Backend

## 3. บัญชีและข้อมูลที่ใช้

| รหัส | ข้อมูลทดสอบ | ใช้ตรวจ |
|---|---|---|
| AUTH-01 | นักศึกษา mock ที่ password ถูกต้อง | Login สำเร็จ, ได้ token และ user role เป็น student |
| AUTH-02 | นักศึกษาเดิมแต่ password ผิด | Login ไม่สำเร็จและไม่สร้าง token/ผู้ใช้ในฐานข้อมูล |
| AUTH-03 | บัญชีที่ TU ตอบว่าไม่ใช่นักศึกษา เช่น employee | ถูกปฏิเสธและไม่สร้าง session |
| AUTH-04 | ไม่มี Authorization header | API ที่ป้องกันตอบ HTTP 401 |
| AUTH-05 | `Bearer invalid-token` | API ที่ป้องกันตอบ HTTP 401 |
| AUTH-06 | token ที่ Logout แล้ว | เรียก `/me` ต่อไม่ได้ ตอบ HTTP 401 |
| AUTH-07 | TU API ล่ม/ตอบผิด/ตั้งค่าไม่ครบ | fail-closed ไม่ออก tokenและไม่สร้าง user บางส่วน |
| AUTH-08 | ฐานข้อมูลบันทึกผู้ใช้ไม่ได้ | Login ตอบ HTTP 503 และไม่ออก token |

## 4. ตารางผลการทดสอบ API/Backend

| รหัส | กรณีทดสอบและข้อมูล | ผลคาดหวัง | ผลจริง | สถานะ | หลักฐาน |
|---|---|---|---|---|---|
| T17-API-01 | Login ด้วยบัญชีนักศึกษาเดิมและ password ที่ถูกต้อง | HTTP 200, ได้ Bearer token, user เป็น student | HTTP 200, ได้ token และ user id/username ถูกต้อง | ผ่าน | `test_login_success_and_status` |
| T17-API-02 | Login ด้วย password ผิด | HTTP 401, ไม่มี token และไม่สร้าง user ใหม่ | HTTP 401, ไม่มี `access_token`, จำนวน User เป็น 0 | ผ่าน | `test_login_rejects_wrong_password` |
| T17-API-03 | Login ซ้ำด้วยบัญชีเดิม | ได้ token ใหม่ แต่ใช้ user database เดิม ไม่สร้าง user ซ้ำ | user id จากการ Login สองครั้งเท่ากัน | ผ่าน | `test_repeated_login_reuses_database_user` |
| T17-API-04 | ตรวจ `/status` ด้วย token จาก Login | `logged_in=true` และคืน user ที่ถูกต้อง | ได้สถานะ Login เป็นจริง | ผ่าน | `test_login_success_and_status` |
| T17-API-05 | เรียก `/me` และ `/logout` โดยไม่มี/มี token ตามกรณี | ไม่มี token ได้ 401; token ถูกต้องใช้ได้; หลัง logout token เดิมใช้ไม่ได้ | Logout สำเร็จ และ `/me` หลัง logout ได้ 401 | ผ่าน | `test_logout_invalidates_token` และ `current_user` |
| T17-API-06 | TU ตอบ false, employee, student แต่ข้อมูลไม่ครบ หรือ network/config ผิด | HTTP 401 และไม่สร้าง session/user | ทุกกรณีตอบ 401 และไม่ persist user | ผ่าน | `test_real_tu_refusal_returns_401_without_persisting_user` (9 subtests) |
| T17-API-07 | Database ใช้งานไม่ได้ระหว่าง Login | HTTP 503 และไม่มี token | HTTP 503 และไม่มี `access_token` | ผ่าน | `test_database_failure_does_not_issue_login_token` |
| T17-API-08 | เรียก Course API โดยไม่มี token/ด้วย token ผิด/ถูก | ไม่มีหรือผิดได้ 401; ถูกจึงค้นหา/อ่านวิชาได้ | ระบบบังคับ Bearer token และชุด Course API ผ่าน | ผ่าน | `test_course_api.py` |
| T17-API-09 | เรียก Guide list/read/filter/publish โดยไม่มี token/ข้อมูลไม่ถูกต้อง | ต้อง Login และไม่บันทึกข้อมูลเมื่อไม่ผ่าน | ตรวจด้วยชุด API test ของ Sprint 1 และไม่พบการข้าม dependency | ผ่าน | `test_publish_guide_api.py`, `test_read_guide_api.py` |
| T17-API-10 | เรียก My Guides โดยไม่มี/ผิด token และเรียกด้วย token ของผู้ใช้ | 401 เมื่อไม่ยืนยัน; เมื่อยืนยันคืนเฉพาะรายการของผู้ใช้ | ผ่านการกรอง owner และกรณีไม่มีรายการคืน array ว่าง | ผ่าน | `test_my_guides_api.py` |
| T17-API-11 | PUT/DELETE รายการของตนเองและของผู้อื่น | เจ้าของทำได้; ผู้ไม่ใช่เจ้าของได้ 404/ไม่เปลี่ยนข้อมูล | update/delete ของเจ้าของผ่าน และของผู้อื่นถูกปฏิเสธ | ผ่าน | `test_my_guide_updates_api.py`, `test_my_guide_deletions_api.py` |

## 5. ตารางผลการทดสอบ Frontend/Proxy

| รหัส | กรณีทดสอบ | ผลคาดหวัง | ผลจริง | สถานะ | หลักฐาน |
|---|---|---|---|---|---|
| T17-UI-01 | หน้า Course ส่งคำขอพร้อม token | ส่ง `Authorization: Bearer ...` ไป Backend | ส่ง header ถูกต้องและ map DTO ได้ | ผ่าน | `course client sends a same-origin authenticated search and maps the DTO` |
| T17-UI-02 | เปิดหน้าค้นหาโดยไม่มี token | ล้าง/ตรวจสถานะและพาไป Login | client redirect เมื่อไม่มี token | ผ่าน | `course client redirects when there is no token` |
| T17-UI-03 | Backend ตอบ 401 ระหว่างค้นหา | ล้าง token และพาไป Login | client ล้าง token และ redirect เมื่อได้ 401 | ผ่าน | `course client clears an expired token and redirects on 401` |
| T17-UI-04 | Proxy ส่งต่อ token และรักษา status error | ไม่กลืน 401/422/404 และไม่สร้าง URL จาก ID ผิดรูปแบบ | ทดสอบ proxy ครบทุกกรณี | ผ่าน | `server.test.js` |
| T17-UI-05 | Login response ผิดรูปแบบหรือ Backend ใช้ไม่ได้ | แสดงข้อความทั่วไป ไม่แสดงข้อมูลลับ | ตรวจเส้นทาง validation/error ใน `login.js` และ syntax ผ่าน | ผ่าน | `node --check frontend/public/js/login.js` |
| T17-UI-06 | เปิดหน้า static โดยตรงโดยไม่มี Login | ไม่ถือว่า static HTML เป็นการอนุญาต API; API ต้องปฏิเสธเอง | สอดคล้องกับการป้องกันที่ dependency `current_user` | ผ่านตามโค้ด; Browser UAT รอทดสอบ | รายการ route ในหัวข้อ 2 |

## 6. ผลการรันทดสอบรวม

### Backend

คำสั่งที่ใช้จากโฟลเดอร์ `backend`:

```powershell
$env:DB_CONNECTION_STRING='sqlite:///:memory:'
$env:PYTHONPATH='.'
$env:TU_API_MODE='mock'
.venv\Scripts\python.exe -m pytest -q test\test_auth.py test\test_course_api.py test\test_my_guides_api.py test\test_my_guide_updates_api.py test\test_my_guide_deletions_api.py test\test_publish_guide_api.py test\test_read_guide_api.py
```

ผลจริง: **60 passed, 1 warning, 23 subtests passed in 1.75s**

คำเตือนเป็น Starlette deprecation warning เรื่อง `httpx`/`httpx2` ไม่ใช่ test failure

### Frontend

คำสั่งที่ใช้จากโฟลเดอร์ `frontend`:

```powershell
& 'C:\Program Files\nodejs\node.exe' --test src/server.test.js src/course-api.test.js src/course-pages.test.js
```

ผลจริง: **13 passed, 0 failed**

## 7. ข้อมูลก่อน/หลังที่ต้องปิดบัง

หลักฐานที่แนบกับรายงานต้องปิดบังสิ่งต่อไปนี้ก่อนส่งให้ PO หรือขึ้น GitHub:

- password ทุกบัญชี
- access token และ Application-Key
- ค่าใน `.env` และ connection string
- ชื่อหรือรหัสบัญชีจริง หากไม่ใช่บัญชีทดสอบที่อนุญาต
- response จาก TU ที่มีข้อมูลส่วนบุคคล

ตัวอย่างการบันทึกที่ปลอดภัย:

```text
ก่อนทดสอบ: ไม่มี token ใน session / บัญชีทดสอบ [ปกปิด]
หลัง Login: ได้ token [ปกปิด] และ role=student
หลัง Logout: เรียก /me ได้ HTTP 401
```

## 8. ข้อจำกัดของหลักฐาน

- Automated test ใช้ SQLite ชั่วคราวและ TU response จำลอง จึงไม่ใช่การยืนยัน TU API จริงหรือฐานข้อมูล Production
- ผล Frontend เป็น Node test และ proxy test; ยังไม่ใช่การตรวจด้วย Chrome ทุกหน้าด้วยมือ
- การเปิด static HTML ได้ไม่ได้แปลว่าผ่านสิทธิ์ เพราะการป้องกันที่ต้องเชื่อถืออยู่ที่ Backend API
- ก่อนตรวจรับจริงควรทำ Browser UAT ซ้ำด้วยบัญชีทดสอบ และแนบภาพที่ปิดข้อมูลลับแล้ว

## 9. ผลตรวจรับของ PO

- ข้อสังเกต/ประเด็นที่ต้องแก้: ____________________________________________________
- ผลตรวจรับ: `รอตรวจ` / `รับรอง` / `ไม่รับรอง`
- ผู้ตรวจ/PO: ______________________________ วันที่: ______________

## 10. ผู้ทดสอบและผู้ตรวจรับควรเป็นใคร

### ผู้ทดสอบ

ควรเป็น Developer หรือ QA/Tester ของทีมที่ไม่ได้เป็นคนแก้โค้ดทุกส่วนของ Login เพียงคนเดียว หากเป็นไปได้ให้มีผู้ทดสอบอีกคนช่วยทดสอบซ้ำ เพราะหน้าที่คือทดลองตามกรณีในตารางจริง ทั้งกรณีผ่านและกรณีปฏิเสธ แล้วบันทึกผลที่เห็นโดยไม่แก้ผลให้ตรงกับที่คาดหวัง

เหตุผลที่เหมาะกับบทบาทนี้:

- เข้าใจวิธีเปิด Frontend/Backend และอ่าน HTTP status ได้
- ทำซ้ำกรณี Login สำเร็จ, password ผิด, token ไม่มี/ผิด และ logout ได้
- ตรวจหลักฐานทางเทคนิค เช่น response status, route และผลจาก test runner ได้
- สามารถปิดบัง password, token และข้อมูลส่วนบุคคลก่อนแนบหลักฐาน

ชื่อที่ควรกรอก: คนที่ลงมือรันทดสอบจริง เช่น `ผู้พัฒนา/QA ของกลุ่ม 4 — __________` ไม่ควรใส่ชื่อคนที่ไม่ได้ทดสอบ

### ผู้ตรวจรับ/PO

ควรเป็น Product Owner หรือผู้รับผิดชอบ User Story U1 ที่ได้รับมอบหมายจากทีม เช่น ผู้ดูแล Sprint/เจ้าของงาน ไม่จำเป็นต้องเป็นคนเขียนโค้ด Login

เหตุผลที่เหมาะกับบทบาทนี้:

- ตรวจว่าการ Login และการป้องกันทุกฟังก์ชันตรงตามความต้องการของผู้ใช้ ไม่ใช่แค่โค้ดไม่ error
- ตัดสินใจได้ว่าผลลัพธ์เพียงพอสำหรับรับงานหรือยัง
- ตรวจว่าบัญชีและข้อมูลที่ใช้สาธิตเหมาะสม และไม่มีข้อมูลลับหลุด
- ลงความเห็น `รับรอง` หรือ `ไม่รับรอง` หลังเห็นผลจริงและหลักฐาน ไม่ใช่เซ็นจากผลคาดหวัง

ถ้าในทีมยังไม่มี PO แยก ให้แต่งตั้งสมาชิกหนึ่งคนเป็นผู้แทน PO อย่างชัดเจน และไม่ควรใช้คนเดียวกันเป็นทั้งผู้ทดสอบและผู้ตรวจรับโดยไม่มีคนทวนซ้ำ

## 11. กรณีทดสอบ TU API จริง

กรณีนี้ต้องใช้ Endpoint, Application-Key และบัญชีทดสอบของ TU ที่ทีมได้รับอนุญาตเท่านั้น ห้ามใช้บัญชีส่วนตัวของสมาชิกโดยไม่ได้รับอนุญาต และห้าม commit ค่าเหล่านี้ลง Git

### ข้อมูลที่ต้องเตรียมในเครื่องทดสอบ

กำหนดไว้ใน `backend/.env` ที่ไม่ถูก commit หรือใน Environment ของ process:

```text
TU_API_MODE=real
TU_API_URL=<Authentication endpoint ที่ TU อนุญาตให้ใช้ทดสอบ>
TU_API_KEY=<Application-Key จาก TU API Developer>
TU_API_TIMEOUT=5
TU_TEST_USERNAME=<บัญชีนักศึกษาทดสอบที่ได้รับอนุญาต>
TU_TEST_PASSWORD=<รหัสผ่านของบัญชีทดสอบ>
```

ตรวจเฉพาะว่าตัวแปรมีค่าหรือไม่ ห้ามพิมพ์ค่าจริงออกหน้าจอ:

```powershell
foreach ($name in 'TU_API_MODE','TU_API_URL','TU_API_KEY','TU_TEST_USERNAME','TU_TEST_PASSWORD') {
  if ([string]::IsNullOrWhiteSpace((Get-Item "Env:$name" -ErrorAction SilentlyContinue).Value)) {
    Write-Host "$name is missing"
  } else {
    Write-Host "$name is configured"
  }
}
```

### วิธีทดสอบแบบไม่บันทึก secret

รันจาก `backend` โดยตั้งค่าลับเฉพาะใน process ปัจจุบัน หรือโหลดจากไฟล์ `.env` ที่ไม่ commit:

```powershell
cd C:\Users\ASUS\Downloads\CS261-Group4-Project-git\backend
& .\.venv\Scripts\python.exe -c @'
import os
from app.services.tu_api import verify_tu_account

username = os.environ["TU_TEST_USERNAME"]
password = os.environ["TU_TEST_PASSWORD"]
account = verify_tu_account(username, password)
print({
    "verified": account is not None,
    "account_type": account.account_type if account else None,
    "username": "[redacted]" if account else None,
})
'@
```

ถ้าใช้ PowerShell รุ่นที่ไม่รองรับ here-string แบบนี้ ให้รันผ่านไฟล์ชั่วคราวที่อยู่นอก Git และลบไฟล์หลังทดสอบ ห้ามใส่ username/password จริงใน command ที่จะถูก copy ไปเป็นหลักฐาน

### ผลที่ต้องบันทึก

| รหัส | ข้อมูลที่ใช้ | ผลคาดหวัง | ผลจริง | สถานะ | หลักฐานที่ปิดข้อมูลลับแล้ว |
|---|---|---|---|---|---|
| T17-REAL-01 | บัญชีนักศึกษาทดสอบที่ TU อนุญาต, endpoint/key ถูกต้อง | TU ตอบนักศึกษาผ่าน; ระบบคืน account type student และ Login สร้าง token | __________________ | ______ | response ที่ลบ username/password/token แล้ว |
| T17-REAL-02 | password ผิด | TU ปฏิเสธ; ระบบตอบ 401 และไม่สร้าง session | __________________ | ______ | status/ข้อความทั่วไปเท่านั้น |
| T17-REAL-03 | บัญชีที่ไม่ใช่นักศึกษา หรือ response ไม่ผ่านเงื่อนไข | ระบบปฏิเสธและไม่ออก token | __________________ | ______ | response ที่ลบข้อมูลส่วนบุคคลแล้ว |
| T17-REAL-04 | ปิด network หรือใช้ endpoint ที่ไม่พร้อม | ระบบ fail-closed ไม่ออก token และไม่แสดง error ลับ | __________________ | ______ | status/เวลา/ข้อความทั่วไป |
| T17-REAL-05 | ไม่มี `TU_API_KEY` หรือ URL ไม่ครบ | ระบบไม่พยายาม Login สำเร็จและตอบ error ที่ควบคุมได้ | __________________ | ______ | ห้ามแนบค่าที่ขาดหรือค่า key |

### สถานะการทดสอบจริงในรอบนี้

รอบการจัดทำรายงานนี้ **ยังไม่ได้เรียก TU API จริง** เพราะ environment ของเครื่องไม่มี `TU_API_URL`, `TU_API_KEY`, `TU_TEST_USERNAME` หรือ `TU_TEST_PASSWORD` ที่พร้อมใช้ และไม่ควรนำ secret มาใส่ในแชตหรือ repository ดังนั้น T17-REAL-01 ถึง T17-REAL-05 ต้องเป็น `รอทดสอบจริง` จนกว่าจะมีบัญชีทดสอบและสิทธิ์จาก TU อย่างถูกต้อง

ผล `60 passed, 23 subtests passed` ในหัวข้อก่อนหน้าเป็นผลจาก SQLite และ mock/response จำลอง ใช้ยืนยัน flow และการ fail-closed เท่านั้น ไม่ควรเขียนแทนผล TU API จริง
