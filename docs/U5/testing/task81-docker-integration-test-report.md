# Task81: ผลทดสอบแก้ไขแนวข้อสอบและย้ายรายวิชาบน Docker

## ขอบเขตและเส้นทางข้อมูล

เพิ่มปุ่มแก้ไขในหน้าของฉันและเชื่อมฟอร์มเดิมกับ PUT /api/my-guides/{guide_id} ผ่าน frontend proxy แบบตายตัว ใช้ Bearer token เดิมและ Backend API/DAO จาก Task72/69 ซึ่งตรวจสิทธิ์เจ้าของใน SQL query ไม่รับเจ้าของจาก browser

ฟอร์มอ่านรายการจาก API, โหลดตัวเลือกรายวิชาจริง และตรวจข้อมูลตาม update DTO: ชื่อ 1–200 ตัวอักษร, หัวข้อ 1–2,000 ตัวอักษร, ปี 1–32767, ภาคเรียน/ช่วงสอบ/รูปแบบตาม enum และจำนวนข้อเป็นจำนวนเต็มบวกหรือเว้นว่าง จำนวนข้อของรูปแบบที่ไม่ใช้จะส่งเป็น null

ระหว่างส่งคำขอปิดการส่งซ้ำและการปิด dialog เมื่อสำเร็จโหลดรายการและตัวเลือกกรองใหม่ เมื่อผิดพลาดคงข้อมูลในฟอร์มและไม่แจ้งว่าสำเร็จ หากเชื่อมต่อขาดหรือ server error ให้ตรวจรายการใหม่ก่อนส่งซ้ำ เพราะอาจบันทึกแล้วแต่ยังไม่ได้รับคำตอบ

## สภาพแวดล้อม

- วันที่ตรวจ: 19 ตุลาคม 2026
- Branch: feat/task81-edit-my-guides (ต่อจาก Task80 commit 6a7e0be)
- Compose project: cs261-task60-test
- Volume: cs261-task60-test_sqlserver_data
- Database: CS261Group4Dev
- Frontend / Backend / SQL Server ports: 25001 / 28001 / 21434
- ใช้บัญชี mock ตาม README และแก้เฉพาะ guide ทดสอบ ID 7

## ผลทดสอบ

| กรณี | หลักฐานและผลจริง | ผล |
|---|---|---|
| เปิดฟอร์มจากหน้าของฉัน | ID 7 โหลดข้อมูลเดิมและรายวิชา CS263 จาก API; มีตัวเลือกวิชา demo 24 วิชา | ผ่าน Browser |
| ชื่อว่างและจำนวนข้อ 0 | แสดงข้อผิดพลาดเฉพาะช่องและไม่ปิดฟอร์ม | ผ่าน Browser และ tests |
| ชื่อยาวเกิน 200 ตัวอักษร | ปฏิเสธก่อนส่ง API | ผ่าน tests |
| ยกเลิกการแก้ไข | เปิดใหม่พบชื่อและข้อมูลเดิม ไม่มีการส่ง update | ผ่าน Browser และ tests |
| แก้ไขและย้ายวิชา | ID 7 ย้าย CS263 ไป CS265, ปี 2568 ภาค 2 กลางภาค, ปรนัย 5 ข้อ อัตนัย null | ผ่าน Browser และ SQL Server |
| กลับหน้าอ่านหลัง reload | URL ใช้ guide=7 และ courseId=14; รายละเอียดเป็นข้อมูลใหม่ | ผ่าน Browser |
| คลังวิชาเดิม/ใหม่ | CS263 แสดงว่าไม่มีแนวข้อสอบ และ CS265 แสดงรายการที่แก้ไข | ผ่าน Browser |
| ไม่สร้างรายการซ้ำหรือเปลี่ยนเจ้าของ | SQL SELECT ก่อนและหลังพบ id=7, publisher_id=2 และจำนวน guides รวมคงที่ 7 แถว | ผ่าน SQL Server |
| ส่งซ้ำและ API ล้มเหลว | ปิดการส่งซ้ำระหว่าง pending; คงค่าฟอร์มเมื่อได้ 502 และไม่เรียก success callback | ผ่าน tests |
| Proxy และ client | PUT ไป path ที่จำกัด ส่ง JSON/token รักษา 401/404/422/500 และตอบ 502 เมื่อ network error; ตรวจ ID ใน response | ผ่าน tests |
| สิทธิ์/validation/rollback ของ Backend | API tests 14 กรณีและ DAO SQLite 4 กรณี | ผ่าน |
| DAO SQL Server | 4 กรณี รวม owner, ย้ายวิชา, non-owner, missing ID และปฏิเสธเปลี่ยนเจ้าของ; สร้าง schema ชั่วคราวแล้ว rollback | ผ่าน |

Frontend suite รวม 40 tests ผ่าน ข้อมูล ID 7 หลังทดสอบมีชื่อ Task81 edit move integration 2026-10-19 และเก็บไว้ใน volume ทดสอบ ไม่มีการเพิ่มหรือลบ guide ในรอบนี้

## วิธีตรวจซ้ำ

รัน frontend tests จาก frontend ด้วย npm.cmd test และรัน Backend tests จาก backend:

    .\.venv\Scripts\python.exe -m pytest -q test/test_my_guide_updates_api.py test/test_update_owned_guide_dao.py

ใช้ override/project ตาม [Task80 runbook](U5_Task80_Docker_Runbook.md) สำหรับ build frontend และเปิดเว็บทดสอบ สำหรับ SQL Server DAO tests รันจาก root repository:

    $testPath = Join-Path (Get-Location) 'backend\test'
    $overridePath = Join-Path $env:TEMP 'cs261-task60-compose.override.yaml'
    docker compose -p cs261-task60-test -f compose.yaml -f $overridePath run --rm --no-deps -e TASK69_TEST_SQLSERVER=1 -v "${testPath}:/app/test:ro" backend python -m unittest discover -s test -p test_update_owned_guide_dao.py -v

## ข้อจำกัด

Browser ใช้บัญชี mock หนึ่งบัญชี กรณีผู้ที่ไม่ใช่เจ้าของตรวจด้วย fixtures ใน API/DAO tests ไม่ได้ใช้บัญชีมหาวิทยาลัยจริงหรือทำ UAT/PO และไม่ได้หยุด Backend จริงเพื่อจำลองความล้มเหลวระหว่าง browser submit

การลบรายการเป็น Task82 ไม่รวมในงานนี้ ไม่มีการเปลี่ยน auth, database schema หรือ backend contract
