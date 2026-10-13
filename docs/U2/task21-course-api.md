Task21: กำหนด API ค้นหาและเปิดดูรายวิชา

API สำหรับผู้ใช้งานทั่วไป

1. ดึงข้อมูลรายวิชาทั้งหมด

GET /courses ใช้สำหรับดึงข้อมูลรายวิชาทั้งหมดที่อยู่ในระบบ

2. ค้นหารายวิชา

GET /courses?search={รหัสหรือชื่อรายวิชา}

ใช้สำหรับค้นหารายวิชาจากรหัสหรือชื่อวิชา เช่น GET /courses?search=CS261


3. เปิดดูรายละเอียดรายวิชา

GET /courses/{course_id} ใช้สำหรับเปิดดูรายละเอียดของรายวิชาหนึ่งรายวิชา เช่น GET /courses/1



ตัวอย่างข้อมูลรายวิชา

{
  "id": 1,
  "course_code": "CS261",
  "course_name": "Software Engineering",
  "description": "วิชาวิศวกรรมซอฟต์แวร์"
}

ระบบจะนำเข้าข้อมูลรายวิชาพื้นฐานโดยทีมงานผ่าน Seed Data

https://docs.google.com/document/d/1dyJ71jzTyS134U_txxCqS6gBuCX0y6eys2LF-HlOJ4E/edit?usp=sharing ลิ้งไฟล์docsสำหรับเปิดอ่าน
