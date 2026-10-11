# Task22: ออกแบบตารางและ Entity รายวิชา

## ตารางสำหรับ Course

| ฟิลด์ | ชนิดข้อมูล | รายละเอียด | เงื่อนไข |
|---|---|---|---|
| `id` | Integer | รหัสภายในระบบ | Primary Key และเพิ่มอัตโนมัติ |
| `course_code` | Varchar(30) | รหัสวิชา เช่น CS261 | ห้ามว่างและห้ามซ้ำ |
| `course_name` | Varchar(255) | ชื่อรายวิชา | ห้ามว่าง |
| `description` | Text | รายละเอียดรายวิชา | ว่างได้ |
| `source` | Varchar(30) | แหล่งที่มาของข้อมูล | `SEED` หรือ `ADMIN` |
| `created_by` | Integer | รหัสผู้เพิ่มข้อมูล | ว่างได้กรณีข้อมูลจาก Seed Data |
| `created_at` | DateTime | วันที่และเวลาที่สร้างข้อมูล | สร้างอัตโนมัติ |
| `updated_at` | DateTime | วันที่และเวลาที่แก้ไขล่าสุด | อัปเดตอัตโนมัติ |

`created_by` เชื่อมกับ `users.id` เมื่อมีตารางผู้ใช้ในระบบ

## ตัวอย่างข้อมูลในตาราง

| id | course_code | course_name | description | source | created_by | created_at | updated_at |
|---:|---|---|---|---|---:|---|---|
| 1 | CS261 | Software Engineering | วิชาวิศวกรรมซอฟต์แวร์ | SEED | NULL | 2026-10-11 20:00:00 | 2026-10-11 20:00:00 |
| 2 | CS230 | Database Systems | วิชาฐานข้อมูล | SEED | NULL | 2026-10-11 20:00:00 | 2026-10-11 20:00:00 |
| 3 | CS399 | New Computer Science Course | รายวิชาใหม่ | ADMIN | 5 | 2026-10-11 20:10:00 | 2026-10-11 20:10:00 |

ความหมายของแหล่งข้อมูล:

- `SEED` = ข้อมูลตั้งต้นที่ทีมเตรียมก่อนเปิดระบบ
- `ADMIN` = ข้อมูลที่ Admin เพิ่มภายหลัง

## โครงสร้าง Entity


Course
├── id
├── course_code
├── course_name
├── description
├── source
├── created_by
├── created_at
└── updated_at


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
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    source: Mapped[str] = mapped_column(
        String(30), nullable=False, default="SEED"
    )
    created_by: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


https://docs.google.com/document/d/1ED9GAX8_YccRXROtNuYREAZHAc5-OlWLRJ83aMESWc4/edit?usp=sharing ลื้งไฟล์docsสำหรับดูและแก้ไข
