# Task7 U1 Sequence Diagram การเข้าสู่ระบบ

แผนภาพอธิบายโค้ดปัจจุบันของการ Login ด้วย TU การสร้างผู้ใช้และ Session รวมถึงการตรวจ token และ Logout ไม่ใช่ผล UAT หรือหลักฐานว่า TU API พร้อมใช้งานตลอดเวลา

ภาพใช้ระดับหน้าที่เพื่อให้อธิบายได้ง่าย: หน้าจอรวม JavaScript และ API client ส่วน API รวม Router กับ Service ภายใน Backend คำขอจาก Browser ยังผ่าน Node proxy และตรวจ Login ตามโค้ดจริง แต่ไม่แยกเป็น lifeline ในภาพ และ DAO ที่รวมไว้หมายถึง DAO หลายคลาสตามตารางอ้างอิง ชื่อ path บนลูกศรใช้ backend endpoint ยกเว้น U5 ที่ทั้งสองชั้นใช้ path เดียวกัน รายละเอียด validation และ error อยู่ในคำอธิบายประกอบ

## เข้าสู่ระบบ

```mermaid
sequenceDiagram
    actor Student as นักศึกษา
    participant UI as หน้า Login
    participant API as Login API
    participant TU as TU API
    participant DAO as UserDAO
    participant DB as ฐานข้อมูล
    Student->>UI: กรอกบัญชี รหัสผ่าน และกดเข้าสู่ระบบ
    UI->>API: login(username, password)
    activate API
    API->>TU: ยืนยันบัญชีนักศึกษา
    TU-->>API: ผลการยืนยัน
    alt ไม่ผ่านการยืนยัน
        API-->>UI: เข้าสู่ระบบไม่สำเร็จ
        UI-->>Student: แจ้งให้ลองใหม่
    else ผ่านการยืนยัน
        API->>DAO: get_or_create_from_tu_profile(...)
        DAO->>DB: ค้นหา User เดิม หรือเพิ่ม User ใหม่
        DB-->>DAO: ข้อมูล User
        DAO-->>API: User
        API->>DB: commit()
        API->>API: สร้าง token และเก็บ Session
        API-->>UI: token และข้อมูลผู้ใช้
        UI-->>Student: เปิดหน้าค้นหารายวิชา
    end
    deactivate API
```

Frontend ปัจจุบันใช้ข้อความ Login ไม่สำเร็จแบบเดียวสำหรับผลปฏิเสธและ upstream failure ไม่ได้แยกเหตุผลทุกกรณีตาม DoD เดิม รหัสผ่านถูกส่งเพื่อยืนยันตัวตน แต่ไม่เก็บในตาราง User หรือข้อมูลโปรไฟล์

TU adapter เลือกชื่อไทยก่อนชื่ออังกฤษเป็น `TUAccount.display_name` แล้ว AuthService ส่งชื่อนี้เข้าพารามิเตอร์ `displayname_en` ในปัจจุบัน จึงไม่ควรอธิบายว่าระบบบันทึกชื่อสองภาษาจาก TU แยกคอลัมน์ครบทุกครั้ง

## ตรวจ Session และออกจากระบบ

```mermaid
sequenceDiagram
    actor Student as นักศึกษา
    participant UI as หน้าเว็บ
    participant API as Auth API
    participant Session as Session ใน Backend
    UI->>API: GET /api/auth/me พร้อม token
    API->>Session: get_user(token)
    Session-->>API: ผู้ใช้ หรือ token ใช้ไม่ได้
    API-->>UI: ข้อมูลผู้ใช้ หรือ 401 ให้ Login ใหม่
    Student->>UI: กดออกจากระบบ
    UI->>API: POST /api/auth/logout พร้อม token
    API->>Session: logout(token)
    Session-->>API: ยกเลิก token แล้ว
    API-->>UI: ออกจากระบบสำเร็จ
    UI-->>Student: ล้าง token และกลับหน้า Login
```

`GET /api/auth/status` ต่างจาก `/me`: เมื่อไม่มี Session ที่ใช้ได้จะตอบ `200 {logged_in:false}` การ restart backend ทำให้ token เดิมใช้ไม่ได้ และ Logout ที่ส่ง token หมดอายุจะถูกปฏิเสธก่อนเข้า handler

## หน้าที่และไฟล์อ้างอิง

- [login.js](../../../frontend/public/js/login.js) ตรวจฟอร์มและเก็บ token ส่วน [profile.js](../../../frontend/public/js/profile.js) โหลดบัญชีและ Logout
- [server.js](../../../frontend/src/server.js) ส่งต่อ auth endpoints และจำกัดเวลารอ upstream
- [auth router](../../../backend/app/routers/auth.py) รับ HTTP และแปลงข้อผิดพลาดเป็น response
- [dependencies.py](../../../backend/app/dependencies.py) ประกอบ dependency และตรวจ Bearer token ผ่าน `current_user`
- [AuthService](../../../backend/app/services/auth.py) ยืนยันบัญชี ควบคุม transaction และเก็บ Session
- [TU adapter](../../../backend/app/services/tu_api.py) เลือกโหมด real หรือ mock
- [UserDAO](../../../backend/app/dao/user_dao.py) เข้าถึง User โดยไม่ commit transaction ของ service
- [แบบ User และ ER](task6-db-er-entity-dao.md)
