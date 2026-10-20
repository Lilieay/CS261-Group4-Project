# ข้อกำหนดของ U2 การค้นหาและเปิดรายวิชา CS

หลัง Login ผู้ใช้เข้าสู่หน้าค้นหารายวิชา เพื่อค้นหาวิชา CS และเปิดแนวข้อสอบผ่าน U3 รายวิชามาจากข้อมูลที่ทีม seed ไว้ ไม่ได้ดึงจาก TU API ทุกครั้งที่ค้นหา

## 1 การค้นหา

1. ค้นหาได้จากรหัสหรือชื่อวิชา โดยไม่แยกตัวพิมพ์ใหญ่เล็ก และตัดช่องว่างหัวท้าย
2. ค้นรหัสจากส่วนต้น เช่น “CS1” พบ CS100 และ CS101 ส่วนชื่อค้นด้วยข้อความบางส่วน เช่น “Software”
3. เมื่อคำค้นว่าง ให้แสดงรายวิชา CS ทั้งหมดในระบบ รวมวิชาที่ยังไม่มีแนวข้อสอบ
4. ผลค้นหาแสดงรหัสตามด้วยชื่อวิชา เช่น “CS261 INTRODUCTION TO SOFTWARE ENGINEERING” และเรียงตามรหัส
5. หากไม่พบ ให้แสดงข้อความว่าไม่พบวิชาในระบบ โดยไม่แสดงรายการเก่า

## 2 รายวิชาหลักสูตรปี 2566

ชุด seed ปัจจุบันมี 24 รายวิชา ไม่รวม CS301, CS303, CS403 และ CS404 ซึ่งเป็นวิชาโครงงานหรือสหกิจศึกษา ดูรายละเอียดข้อมูลตั้งต้นใน [Task26](../runbooks/task26-course-seed-data.md)

| รหัสวิชา | ชื่อวิชา |
| :---- | :---- |
| CS100 | BASIC WEB DEVELOPMENT  |
| CS101 | DISCRETE STRUCTURES |
| CS102 | PROBLEM SOLVING BASICS AND COMPUTER PROGRAMMING |
| CS103 | INTRODUCTION TO COMPUTER PROGRAMMING |
| CS104 | INTRODUCTION TO COMPUTER PROGRAMMING USING PYTHON |
| CS213 | DATA STRUCTURES |
| CS221 | INTRODUCTION TO COMPUTER SYSTEM AND ORGANIZATION |
| CS223 | VIRTUALIZATION TECHNOLOGY |
| CS224 | LINUX ADMINISTRATION AND PERFORMANCE MONITORING |
| CS240 | PRINCIPLES OF DATA SCIENCE |
| CS241 | PROGRAMMING LANGUAGES AND PARADIGMS |
| CS261 | INTRODUCTION TO SOFTWARE ENGINEERING |
| CS263 | SOFTWARE REQUIREMENT SPECIFICATION |
| CS265 | BASIC MOBILE DEVELOPMENT |
| CS331 | NET-CENTRIC COMPUTING |
| CS341 | BIG DATA ENGINEERING |
| CS345 | PRACTICAL MACHINE LEARNING |
| CS346 | BIG DATA APPLICATIONS AND ANALYTICS |
| CS361 | CLOUD-BASED SOFTWARE ARCHITECTING |
| CS364 | MOBILE APPLICATION DEVELOPMENT |
| CS373 | ADVANCED SEARCH STRATEGIES |
| CS374 | NATURAL LANGUAGE PROCESSING |
| CS384 | HUMAN \- COMPUTER INTERACTION |
| CS440 | SELECTED TOPICS IN DATA SCIENCE |

## 3 การเปิดหน้ารายวิชา

เมื่อเลือกผลค้นหา ต้องเปิดวิชาที่เลือก พร้อมรหัส ชื่อวิชา และรายการแนวข้อสอบตาม U3 หากยังไม่มีแนวข้อสอบ ต้องเปิดหน้าวิชาได้และแสดงข้อความว่ายังไม่มีแนวข้อสอบสำหรับวิชานี้

หน้าจอปัจจุบันซ่อนผู้สอน เพราะข้อมูลตั้งต้นยังไม่มีชื่อผู้สอน ฟิลด์ `instructor_name` ยังคงอยู่ใน API และรับค่า `null` ได้

ส่วนสรุปเป็นงาน Sprint 2 รูปแบบคำขอและคำตอบของการค้นหาและเปิดวิชาดู [Task21](../design/task21-course-api.md)
