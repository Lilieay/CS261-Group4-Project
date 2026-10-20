# Task21 U2 API ค้นหาและเปิดรายวิชา

API นี้ใช้กับนักศึกษาที่ Login แล้ว รายวิชามาจาก seed ของทีม การค้นหาไม่สร้างข้อมูลใหม่ และคืนเฉพาะรายวิชาที่รหัสขึ้นต้น CS

## เส้นทาง

| Browser เรียก Node proxy | Backend รับ | ผลสำเร็จ |
|---|---|---|
| GET `/api/courses` | GET `/courses` | array ของ CourseDTO |
| GET `/api/courses?search=CS261` | GET `/courses?search=CS261` | array ของ CourseDTO ที่ตรงคำค้น |
| GET `/api/courses/1` | GET `/courses/1` | CourseDTO หนึ่งรายการ |

ทุกคำขอต้องส่ง `Authorization: Bearer <access_token>` ตารางต่อไปนี้อธิบาย contract ของ backend ส่วน proxy ส่งต่อผล HTTP และอาจตอบ 502 เมื่อเชื่อม backend ไม่ได้

## ค้นหารายวิชา

```http
GET /courses?search=CS261
Authorization: Bearer <access_token>
```

search เป็นข้อความยาวไม่เกิน 255 ตัวอักษร ไม่ส่ง search หรือส่งช่องว่างล้วนจะได้รายวิชา CS ทั้งหมด รวมวิชาที่ไม่มีแนวข้อสอบ ค้นรหัสจากส่วนต้นและไม่สนตัวพิมพ์ใหญ่เล็ก ค้นชื่อด้วยข้อความบางส่วน ผลเรียงตาม course_code

ตัวอย่างข้อมูลสมมติ:

```json
[
  {
    "id": 1,
    "course_code": "CS261",
    "course_name": "INTRODUCTION TO SOFTWARE ENGINEERING",
    "instructor_name": null,
    "description": null
  }
]
```

ไม่พบผลค้นหาตอบ `200 []` ไม่ใช่ 404

## เปิดรายวิชา

```http
GET /courses/1
Authorization: Bearer <access_token>
```

course_id ต้องเป็นจำนวนเต็มบวก ผลสำเร็จ `200` เป็น object แบบเดียวกับหนึ่งรายการในตัวอย่างค้นหา หาก ID ไม่มีหรือไม่ใช่รายวิชา CS ตอบ 404 ส่วนวิชาที่มีอยู่แต่ยังไม่มีแนวข้อสอบยังเปิดได้

## CourseDTO

| ฟิลด์ | ชนิดและความหมาย |
|---|---|
| `id` | integer คีย์ภายในของรายวิชา |
| `course_code` | string รหัสวิชา |
| `course_name` | string ชื่อวิชา |
| `instructor_name` | string หรือ null ข้อมูลผู้สอนที่ระดับรายวิชา |
| `description` | string หรือ null รายละเอียดรายวิชา |

ไม่มี instructor_name_2 ใน DTO ข้อมูลผู้สอนยังส่งผ่าน API แต่หน้าเว็บปัจจุบันไม่แสดงส่วนนี้

## ข้อผิดพลาด

| HTTP | `error.code` | กรณี |
|---|---|---|
| 401 | AUTH_REQUIRED | ไม่มี Session ที่ใช้ได้ |
| 404 | COURSE_NOT_FOUND | เปิดรายวิชาที่ไม่พบหรืออยู่นอกกลุ่ม CS |
| 422 | INVALID_PARAMETERS | path/query ไม่ผ่าน validation |
| 500 | INTERNAL_ERROR | ข้อผิดพลาดที่ CourseApiRoute จัดการ |

```json
{"error":{"code":"COURSE_NOT_FOUND","message":"ไม่พบรายวิชา","fields":[]}}
```

## การแบ่งหน้าที่

Courses Router รับ request และเรียก CourseService ส่วน service แปลง Course เป็น CourseDTO โดยใช้ CourseDAO ค้นข้อมูล current_user ตรวจ Login และ CourseApiRoute จัดรูปแบบ error

ดู [CourseDTO](../../../backend/app/schemas/courses.py), [Courses Router](../../../backend/app/routers/courses.py), [CourseService](../../../backend/app/services/courses.py), [CourseDAO](../../../backend/app/dao/course_dao.py) และ [Sequence Task23](task23-course-search-sequence-diagram.md)
