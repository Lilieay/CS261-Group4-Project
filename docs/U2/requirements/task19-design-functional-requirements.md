# ข้อกำหนดของ U2: ค้นหารายวิชา CS ด้วยรหัสหรือชื่อและเปิดหน้ารายวิชา

อ้างอิงจาก U2\_Story Detail

ให้หน้าค้นรายวิชานี้ เป็นหน้าแรกหลังจากที่ User เข้าสู่ระบบเรียบร้อยแล้ว โดยที่หน้าค้นหารายวิชาเอาไว้สำหรับค้นหารายวิชาที่ผู้ใช้ต้องการเข้าไปดูแนวข้อสอบหรือสรุป

## 1\. การค้นหา

	1.1 จะสามารถค้นหาผ่านรหัสวิชา และชื่อได้   
	1.2 การค้นหาจะไม่แยกตัวพิมใหญ่หรือเล็ก เช่น ค้นหา cs261 \= CS261 , introduction \= Introduction  
	1.3 การค้นหาด้วยรหัสวิชา จะสามารถค้นหาด้วยอักษรขึ้นต้นของรหัสวิชาได้ เช่น ค้นหา “CS1” จะขึ้นผลลัพธ์ของรายวิชาเช่น CS100, CS101   
	1.4 การค้นหาด้วยชื่อวิชา สามารถค้นหาด้วยบางส่วนของชื่อได้ เช่น ค้นหา “Intro” จะแสดงรายวิชาที่มีคำว่า Intro, ค้นหา “Software”  จะแสดงรายวิชาที่มีคำว่า Software  
	1.5 การค้นหาจะตัดช่องว่างหัวท้ายด้วย เช่น ค้นหา  “ CS261 ” ผลลัพธ์การค้นหาก็จะเหมือนกันกับ “CS261”  
	1.6 ถ้าคำค้นหาว่าง จะแสดงทุกรายวิชาที่มีในระบบ  
	1.7 เมื่อค้นหารายวิชา ไม่ว่าจะด้วยรหัส หรือชื่อ รายการรายวิชาที่แสดงก็จะขึ้นต้นด้วยรหัส และตามด้วยชื่อวิชาเสมอ เช่น “CS261 INTRODUCTION TO SOFTWARE ENGINEERING”  
	1.8 ถ้าค้นหารายวิชาแล้วไม่เจอในระบบ ก็จะไม่แสดงรายวิชาใด ๆ พร้อมมีข้อความบอกว่า “ไม่พบวิชาในระบบ”  
	1.9 รายวิชาที่ไม่มีแนวข้อสอบหรือสรุป จะยังสามารถค้นหาได้

## 2\. รายวิชาทั้งหมดใน CS เฉพาะหลักสูตรปี 66

เป็นรายวิชาที่จะเตรียมไว้ในระบบ

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
| CS301 | PREPARATION FOR SENIOR PROJECTS AND CO-OPERATIVE EDUCATION |
| CS303 | SPECIAL PROJECTS 1 |
| CS331 | NET-CENTRIC COMPUTING |
| CS341 | BIG DATA ENGINEERING |
| CS345 | PRACTICAL MACHINE LEARNING |
| CS346 | BIG DATA APPLICATIONS AND ANALYTICS |
| CS361 | CLOUD-BASED SOFTWARE ARCHITECTING |
| CS364 | MOBILE APPLICATION DEVELOPMENT |
| CS373 | ADVANCED SEARCH STRATEGIES |
| CS374 | NATURAL LANGUAGE PROCESSING |
| CS384 | HUMAN \- COMPUTER INTERACTION |
| CS403 | SPECIAL PROJECTS 2 |
| CS404 | CO-OPERATIVE EDUCATION 2 |
| CS440 | SELECTED TOPICS IN DATA SCIENCE |

## 3\. การเปิดอ่านหน้ารายวิชา

 	3.1 หลังจากผู้ใช้ค้นหารายวิชาเสร็จ และกดเลือกเปิดหน้ารายวิชา ก็จะเข้าสู่หน้ารายวิชาซึ่งในหน้ารายวิชานี้ จะมีให้เลือกเป็นต้องการดูแนวข้อสอบ (เชื่อมกับ U3) หรือสรุป (ทำใน sprint 2\)  
3.2 รายวิชาที่ยังไม่มีแนวข้อสอบหรือสรุป จะยังสามารถเปิดเข้าสู่หน้ารายวิชาได้และระบบแจ้งว่า “ยังไม่มีเนื้อหาในรายวิชานี้”  
3.3 หน้ารายวิชาที่เปิดขึ้นมา จะแสดงรายละเอียดคือ 

1. รหัสและชื่อวิชา ของวิชาที่กดเปิด  
2. ชื่ออาจารย์ผู้สอนจากข้อมูลพื้นฐานรายวิชาหลักสูตร 2566 ที่ระบบเตรียมไว้   
3. หน้ากรองเลือกแนวข้อสอบตาม  U3  
4. หน้าเลือกสรุป (sprint 2\)

   