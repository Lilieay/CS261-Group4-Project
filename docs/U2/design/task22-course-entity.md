# Task22: ออกแบบตารางและ Entity รายวิชา

## ตารางสำหรับ Course

| ฟิลด์ | ชนิดข้อมูล | รายละเอียด | เงื่อนไข |
|---|---|---|---|
| `id` | Integer | รหัสภายในระบบ | Primary Key และเพิ่มอัตโนมัติ |
| `course_code` | Varchar(30) | รหัสวิชา เช่น CS261 | ห้ามว่างและห้ามซ้ำ |
| `course_name` | Varchar(255) | ชื่อรายวิชา | ห้ามว่าง |
| `instructor_name` | Varchar(255) | ชื่ออาจารย์ผู้สอน | ว่างได้|
| `description` | Text | รายละเอียดรายวิชา | ว่างได้ |
 


## ตัวอย่างข้อมูลในตาราง

| id | course_code | course_name | instructor_name  | description | 
|---:|---|---|---|---|
| 1 | CS261 | Software Engineering | songsakdi rongviriyapanish,theepprakorn rakfaen |  วิชาวิศวกรรมซอฟต์แวร์   |
| 2 | CS230 | Database Systems | -  |  วิชาฐานข้อมูล  |



 โครงสร้าง Entity


Course
├── id
├── course_code
├── course_name
├── instructor_name 
├── description



 Entity ใน Python

Entity `Course` ใช้ SQLAlchemy แทนตาราง `courses` ในฐานข้อมูล


from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    course_code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    course_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    instructor_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
  


https://docs.google.com/document/d/1ED9GAX8_YccRXROtNuYREAZHAc5-OlWLRJ83aMESWc4/edit?usp=sharing ลื้งไฟล์docsสำหรับดูและแก้ไข
