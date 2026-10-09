# แนวทางใช้ Git สำหรับทีม

Workflow ของทีม: เลือก task > แตก branch งาน > implement และทดสอบ > PR/review เข้า `integration/sprint1` > ทำ task integration และ UAT > PR/review เข้า `main` > ติด tag เวอร์ชัน Demo

## บทบาทของแต่ละ branch

| Branch | ใช้ทำอะไร | เกณฑ์รวมงาน |
| --- | --- | --- |
| `main` | ฐานของเวอร์ชันที่ทดสอบแล้วและพร้อม Demo | ผ่าน integration, เกณฑ์รับงาน และการตรวจรอบส่งมอบ |
| `integration/sprint1` | รวมโค้ดทุกส่วนที่เลือกทำใน Sprint 1 | รับ PR ของ task ที่ผ่าน review และการทดสอบตามขอบเขตงาน |
| `feat/task5-login-ui` และ branch งานอื่น | พัฒนาแต่ละชุดงาน เช่น frontend, backend หรือ DAO | รวมเข้า integration branch เมื่อพร้อมให้ทดสอบร่วมกับส่วนอื่น |

รอบถัดไปสร้าง `integration/sprint2` จาก `main` เวอร์ชันล่าสุด แล้วทำแบบเดียวกัน
ใช้ integration branch ร่วมกันหนึ่งอันต่อ Sprint เพื่อให้มีจุดตรวจ frontend/backend/database ร่วมกัน
`integration/...` เป็นชื่อ branch สำหรับรวมงาน ส่วน type ของ commit ยังเลือกตามการเปลี่ยนแปลง เช่น `fix`, `test` หรือ `chore`

คำสั่งทั้งหมดรันจากราก repo และชื่อ branch ในตัวอย่างให้เปลี่ยนตามงานที่รับผิดชอบ

## 1. แตก branch ต่อ task

branch งานแตกจาก integration branch ของ Sprint ปัจจุบัน ส่วนชื่อ branch บอกสิ่งที่จะทำ
branch หนึ่งมีไฟล์ทั้ง repo เหมือนเดิม ชื่อ `login-ui` หรือ `login-api` บอกขอบเขตงาน ไม่ได้จำกัดสิทธิ์แก้ไฟล์ตามโฟลเดอร์

รูปแบบชื่อ branch ที่แนะนำคือ `<type>/<task>-<short-description>` เช่น `feat/task5-login-ui`
ใช้ตัวพิมพ์เล็ก คั่นคำด้วย `-` และใส่เลข task เมื่อมีงานใน board ให้เชื่อมโยง
งานแก้บั๊กที่ยังไม่มีเลข task ใช้ชื่ออย่าง `fix/login-button` ได้

### ประเภทงาน: feat, fix, chore และอื่น ๆ

ใช้ชื่อประเภทงานชุดเดียวกันในการตั้ง branch และ commit โดยทีมกำหนดความหมายดังนี้:

| Type | ความหมาย | ใช้เมื่อ | ตัวอย่าง commit |
| --- | --- | --- | --- |
| `feat` | feature: เพิ่มความสามารถ | เพิ่มหน้าจอหรือ API ใหม่ | `feat(task5): add login form` |
| `fix` | แก้ข้อผิดพลาด | แก้สิ่งที่ควรทำงานอยู่แล้วแต่ทำงานผิด | `fix(frontend): correct button element lookup` |
| `chore` | งานเตรียมและดูแลโปรเจกต์ | เพิ่ม `.gitignore` หรือ config เครื่องมือพัฒนา | `chore(task2): ignore local environment files` |
| `docs` | documentation: เอกสาร | เขียน README, คู่มือ หรือ API spec | `docs(task2): document local setup` |
| `refactor` | ปรับโครงสร้างโค้ด | ย้ายหรือจัดโค้ดโดยพฤติกรรมเดิมยังเหมือนเดิม | `refactor(backend): extract login validation` |
| `test` | งานทดสอบ | เพิ่มหรือปรับ test cases และโค้ดทดสอบ | `test(task6): cover invalid credentials` |
| `style` | รูปแบบการเขียนโค้ด | จัด indent หรือ whitespace โดยไม่เปลี่ยนพฤติกรรม | `style(frontend): format login script` |
| `perf` | performance: ประสิทธิภาพ | ปรับให้ทำงานเร็วขึ้นโดยคงผลลัพธ์เดิม | `perf(backend): optimize course search query` |
| `build` | dependencies และระบบ build | เพิ่มหรืออัปเดต package หรือ config การ build | `build(frontend): update Express dependency` |
| `ci` | continuous integration: ตรวจงานอัตโนมัติ | เพิ่มหรือปรับ GitHub Actions | `ci: run backend checks on pull requests` |

เลือก type จากผลของการเปลี่ยนแปลง ไม่ใช่จากนามสกุลไฟล์
เช่น เพิ่ม CSS ให้หน้า Login ใหม่เป็นส่วนหนึ่งของ `feat`; แก้ CSS ที่ทำให้ปุ่มกดไม่ได้เป็น `fix`
`style` ในคู่มือนี้หมายถึงการจัดรูปแบบโค้ด ไม่ได้หมายถึงการตกแต่งหน้าเว็บทุกกรณี

Conventional Commits กำหนดความหมายหลักของ `feat` และ `fix` และอนุญาตประเภทอื่นได้; รายการอื่นในตารางเป็นข้อตกลงที่เสนอให้ทีมใช้

| งาน | ตัวอย่าง branch |
| --- | --- |
| Task5: หน้า Login | `feat/task5-login-ui` |
| Task6: Login API | `feat/task6-login-api` |
| Task7: User Entity/DAO | `feat/task7-user-dao` |
| Task3: Docker | `chore/task3-docker` |
| แก้ปุ่ม Login ไม่ตอบสนอง | `fix/login-button` |
| Task2: README และแนวทาง Git | `docs/task2-setup-guide` |

แตก branch ต่อชุดงานที่มีเป้าหมายเดียวและตรวจรับร่วมกันได้ โดยปกติใช้หนึ่ง branch ต่อ task แต่ task ที่ต้องเปลี่ยนพร้อมกันสามารถอยู่ branch เดียวกันได้
branch งานจบเมื่อรวมเข้า integration branch แล้ว งานชิ้นถัดไปให้แตกจาก integration branch ล่าสุด
งานหนึ่งที่ต้องแก้ทั้ง frontend และ backend สามารถอยู่ branch เดียวกันได้ ถ้ามีเป้าหมายเดียวและรีวิวร่วมกันได้

## 2. ก่อนเริ่มงาน

เลือก card ใน Trello ใส่ผู้รับผิดชอบและย้ายเข้า In Progress แล้วตรวจสถานะ Git:

```powershell
git status
git branch --show-current
```

ถ้ามีไฟล์งานค้าง ให้ commit งานที่เกี่ยวข้องบน branch เดิมก่อนเปลี่ยน branch
ไฟล์ untracked ที่ต้องเก็บไว้ต้องตรวจแยกด้วย เพราะยังไม่อยู่ใน commit

### เตรียม integration branch ครั้งแรกของ Sprint

ให้ผู้ประสานงานหนึ่งคนทำครั้งเดียวจากฐานเริ่มต้นที่ทีมตกลง หรือ `main` เวอร์ชัน Demo ล่าสุด โดย working tree พร้อม:

```powershell
git switch main
git pull --ff-only origin main
git switch -c integration/sprint1
git push -u origin integration/sprint1
```

### สมาชิกนำ integration branch มาใช้ครั้งแรก

เพื่อนที่ยังไม่มี repo ให้ clone branch พัฒนาโดยตรง:

```powershell
git clone --branch integration/sprint1 https://github.com/Lilieay/CS261-Group4-Project.git
cd CS261-Group4-Project
```

คำสั่งนี้มี local branch `integration/sprint1` พร้อมแล้ว ให้ติดตั้งตาม README และใช้หัวข้อเริ่ม task ใหม่ด้านล่าง

สำหรับเครื่องที่มี repo อยู่แล้ว แต่ยังไม่มี local branch ชื่อนี้:

```powershell
git fetch origin
git switch --track origin/integration/sprint1
```

### เริ่ม task ใหม่

เมื่อมี local integration branch แล้ว ให้อัปเดตและแตก branch งาน:

```powershell
git switch integration/sprint1
git pull --ff-only origin integration/sprint1
git switch -c feat/task5-login-ui
```

`git switch -c` สร้าง branch ใหม่และเปลี่ยนไปทำงานบน branch นั้น
`--ff-only` อัปเดตเมื่อทำได้โดยไม่สร้าง merge commit; ถ้าขึ้นว่า fast-forward ไม่ได้ ให้ตรวจประวัติร่วมกับทีมก่อนดำเนินการต่อ
ก่อนให้เพื่อนแตก branch ให้ตรวจว่าโค้ดตั้งต้นและเอกสารที่ต้องใช้ถูก commit และ push บน integration branch ครบแล้ว เพื่อให้ทุกคนเริ่มจากฐานเดียวกัน

## 3. Implement และบันทึก commit

แก้โค้ดและทดสอบพฤติกรรมของ task ให้ผ่าน จากนั้นตรวจสิ่งที่เปลี่ยน:

```powershell
git status
git diff
```

เลือก stage เฉพาะไฟล์ของงาน ตัวอย่างสำหรับหน้า Login หลังจากสร้างไฟล์เหล่านี้แล้ว:

```powershell
git add frontend/public/pages/login.html frontend/public/css/login.css frontend/public/js/login.js
git diff --cached
git commit -m "feat(task5): add login form and validation"
```

ตัวอย่างนี้ใช้ชื่อไฟล์สมมติของงาน Login; ให้ระบุ path ของไฟล์ที่คุณสร้างหรือแก้จริง
`git diff` แสดงการแก้ไฟล์ tracked ที่ยังไม่ได้ stage ส่วน `git diff --cached` แสดงสิ่งที่จะบันทึกใน commit
`git status` ใช้ตรวจทั้งไฟล์ที่แก้ ไฟล์ใหม่ และไฟล์ที่ลบ

### รูปแบบข้อความ commit

ใช้รูปแบบนี้สำหรับ commit ที่เขียนเอง:

```text
<type>(<scope>): <description>
```

- `type`: ประเภทงานจากตารางด้านบน เช่น `feat`, `fix`, `chore` หรือ `docs`
- `scope`: งานหรือส่วนที่แก้ ใช้ `task5`, `task6` เมื่อเกี่ยวข้องกับ task; ถ้าไม่มีเลข task ใช้ `frontend`, `backend` หรือ `db`
- `description`: สรุปว่าเปลี่ยนอะไรให้เห็นผลชัดเจน โดยทีมแนะนำภาษาอังกฤษและเริ่มด้วยคำกริยา เช่น `add`, `fix`, `document` หรือ `update`

ตัวอย่าง `feat(task5): add login form` หมายถึงเพิ่มฟีเจอร์ใน Task5 โดยสิ่งที่เพิ่มคือฟอร์ม Login
มีช่องว่างหนึ่งตัวหลัง `:`; เครื่องหมาย `< >` เป็นเพียง placeholder ไม่ต้องพิมพ์ในข้อความจริง
Scope เป็นส่วนที่เลือกใส่ได้ตาม Conventional Commits; คู่มือนี้แนะนำให้ใส่เมื่อระบุ task หรือส่วนที่แก้ได้
งานทั้ง repo ที่ไม่ต้องระบุ scope ใช้ `chore: configure development tools` ได้

ตัวอย่างคำสั่งจริง:

```powershell
git commit -m "feat(task5): add login form and validation"
git commit -m "fix(frontend): correct button element lookup"
git commit -m "chore(task2): ignore local environment files"
git commit -m "docs(task2): document setup and Git workflow"
```

แต่ละบรรทัดเป็นตัวอย่างสำหรับงานคนละประเภท ให้เลือกคำสั่งที่ตรงกับไฟล์ที่ stage ไว้ ไม่ต้องรันครบทุกบรรทัด
เขียนให้คนอ่านรู้สิ่งที่เปลี่ยน เช่น `fix(frontend): serve CSS and JavaScript assets` แทนข้อความกว้าง ๆ อย่าง `update code` หรือ `done`

หนึ่ง commit ควรมีการเปลี่ยนแปลงที่เกี่ยวข้องกันและอธิบายผลได้ แต่หนึ่ง task มีหลาย commit ได้
เช่น branch `feat/task5-login-ui` อาจมี commit ทั้ง `feat` และ `fix` ตามงานที่ทำในแต่ละรอบ:

```text
feat(task5): add login page layout
feat(task5): submit login form to backend
fix(task5): display invalid credential error
docs(task2): document setup and Git workflow
```

ถ้าต้องอธิบายเหตุผลหรือข้อจำกัดเพิ่มเติม สามารถเพิ่ม body หลังบรรทัดสรุป โดยเว้นบรรทัดว่างก่อน body
ถ้าเปลี่ยน API จนโค้ดที่ใช้อยู่ต้องปรับตาม ให้ระบุ `!` ก่อน `:` เช่น `feat(task6)!: rename login request field` และอธิบายวิธีปรับตามใน body/PR
รูปแบบนี้เป็นข้อตกลงของทีมที่เสนอให้ใช้ ไม่ใช่ข้อบังคับของ Git หรือ Scrum และยังไม่มีเครื่องมือบังคับรูปแบบใน repo
เก็บ `package-lock.json` เมื่อ dependencies เปลี่ยน ส่วน `.env`, `node_modules` และ virtual environment ให้คงไว้เฉพาะในเครื่องตาม `.gitignore`

## 4. Push และเปิด Pull Request

ครั้งแรกที่ push branch:

```powershell
git push -u origin feat/task5-login-ui
```

ครั้งถัดไปบน branch เดิมใช้:

```powershell
git push
```

Commit บันทึกประวัติในเครื่อง ส่วน push ส่ง commit ไป GitHub; push อย่างเดียวยังไม่รวมงานเข้า `main`

เปิด repo ใน GitHub > Pull requests > New pull request แล้วเลือก:

- **base:** `integration/sprint1` ซึ่งเป็น branch ที่จะรับงานของ Sprint นี้
- **compare:** branch ของคุณ เช่น `feat/task5-login-ui`

ใส่รายละเอียด PR ให้เพื่อนตรวจได้:

```text
Task: Task5 / U1 - หน้า Login
Trello: <ลิงก์ card>

สิ่งที่เปลี่ยน:
- เพิ่มฟอร์ม Login และการตรวจช่องว่าง
- แสดงข้อผิดพลาดจาก API

วิธีตรวจและผล:
- เปิดหน้าฟอร์ม: ผ่าน
- ส่งฟอร์มที่ช่องว่าง: แสดงข้อผิดพลาด
- เชื่อม backend จริง: ยังรอ Task6
```

ระบุผลที่ทดสอบจริง ถ้ายังใช้ mock หรือรออีก task ให้เขียนชัดเจนและเปิดเป็น Draft PR ได้
ส่งให้เพื่อนอย่างน้อยหนึ่งคน review ตามข้อตกลงทีม แล้วแก้ feedback ด้วย commit ใหม่บน branch เดิมและ push อีกครั้ง; PR จะอัปเดตตาม branch

## 5. เมื่อ frontend และ backend ทำพร้อมกัน

ให้ทั้งสองคนเริ่มจาก `integration/sprint1` ล่าสุด แล้วแยกงาน เช่น:

```text
integration/sprint1
├── feat/task5-login-ui   -> PR กลับเข้า integration/sprint1
├── feat/task6-login-api  -> PR กลับเข้า integration/sprint1
└── feat/task7-user-dao   -> PR กลับเข้า integration/sprint1
```

ก่อน implement ให้ตกลง API ร่วมกัน: method/URL, fields ของ request, รูปแบบ response/error และวิธีส่งหรือเก็บสถานะ Login
บันทึกข้อตกลงในเอกสาร API ของทีมแล้วแนบลิงก์ใน card/PR เพื่อให้ทั้งสองฝั่งอ้างอิงตรงกัน
ตอนนี้ repo ยังไม่มี Login API spec; endpoint และชื่อ fields ต้องออกแบบใน Task1 ก่อนใช้จริง

Frontend สามารถใช้ mock ตาม spec ระหว่างรอ backend โดยระบุว่าผลไหนใช้ mock และทดสอบใหม่กับ API จริงเมื่อรวมงาน
ถ้าฝั่งหนึ่งเสร็จและผ่าน review ก่อน ให้ merge เข้า `integration/sprint1`
เมื่ออีกฝั่งต้องใช้ API/โค้ดที่เพิ่งรวม หรือแก้ conflict ก่อนเปิด PR ให้นำ integration branch ล่าสุดเข้ามาใน branch งานของตัวเอง:

```powershell
git switch feat/task5-login-ui
git status
git fetch origin
git merge origin/integration/sprint1
```

ก่อน merge ต้องบันทึกงานค้างให้เรียบร้อย แล้วทดสอบ frontend/backend ร่วมกันหลัง merge
ถ้ามีการเปลี่ยน `package-lock.json` หรือ `backend/requirements.txt` ให้ติดตั้ง dependencies ตาม README อีกครั้ง
ถ้า PR ต้องใช้โค้ดจากอีก branch ที่ยังไม่ merge ให้ระบุ dependency ใน PR และให้ทีมตกลงลำดับรวมงาน

การ merge task เข้า integration branch เป็นจุดเริ่มตรวจการทำงานร่วมกัน ไม่ได้หมายความว่า User Story ผ่าน DoD แล้ว
เริ่มทดลองเชื่อมกันระหว่างพัฒนาได้ ส่วน task integration จบเมื่อมีผลตรวจครบตามเกณฑ์ของงานนั้น
เช่น Task8 ตรวจ Login จาก UI ผ่าน API/DAO บน Docker พร้อมหลักฐานตาม board; Task15 ตรวจการค้นหารายวิชาเมื่อรวมระบบแล้ว
ปัญหาที่พบระหว่างรวมงานให้แตก branch เช่น `fix/task8-login-integration` จาก integration branch แล้วเปิด PR กลับเข้าที่เดิม

## 6. เมื่อเกิด merge conflict

Git จะแสดงไฟล์ที่ชนกัน ให้เริ่มจาก:

```powershell
git status
```

เปิดไฟล์ที่มี conflict แล้วคุยกับผู้แก้อีกฝั่งเพื่อเลือกหรือรวมพฤติกรรมที่ถูกต้อง
ลบ markers `<<<<<<<`, `=======` และ `>>>>>>>` เมื่อแก้เสร็จ แล้วทดสอบก่อนบันทึกผล merge:

```powershell
git add <path-of-resolved-file>
git commit
git push
```

แทน `<path-of-resolved-file>` ด้วย path จริง; เครื่องหมาย `< >` เป็นเพียง placeholder ในตัวอย่าง
ถ้ายังไม่พร้อมแก้ conflict ของ merge ที่กำลังทำ สามารถใช้ `git merge --abort` เพื่อยกเลิก merge ครั้งนั้นแล้ววางแผนใหม่

## 7. หลัง PR ผ่าน review และ merge

ผู้รวมงานตรวจผลการทดสอบแล้วกด Merge pull request เข้า `integration/sprint1` บน GitHub
สำหรับเริ่มต้น ให้ทีมใช้ Create a merge commit เพื่อเก็บ commit ของ branch งานไว้ และใช้รูปแบบนี้ให้สม่ำเสมอ

เมื่อ PR merge แล้ว ให้กลับมาอัปเดตเครื่อง:

```powershell
git switch integration/sprint1
git pull --ff-only origin integration/sprint1
```

ตรวจว่า working tree พร้อมก่อนเปลี่ยน branch; งานที่แก้หลัง commit ล่าสุดต้องบันทึกบน branch งานก่อน
ทดสอบโค้ดที่รวมแล้ว จากนั้นลบ remote branch ด้วยปุ่ม Delete branch ใน PR ที่ merge แล้ว
ถ้าต้องการลบ branch ในเครื่องด้วย ใช้ชื่อ branch ที่จบงานแล้ว:

```powershell
git branch -d feat/task5-login-ui
```

ถ้า Git แจ้งว่ายังไม่ merge ให้ตรวจ PR และประวัติก่อนลบ
แนบ PR และผลทดสอบใน Trello แล้วเปลี่ยนสถานะตามเกณฑ์รับงานที่ทีมตกลง
PR merge แล้วไม่ได้แปลว่า User Story ผ่าน DoD อัตโนมัติ เช่น งาน UI ที่ใช้ mock ยังต้องมีผลรวมระบบจริงตาม task

## 8. รวมเวอร์ชัน Demo เข้า main

เมื่อ task integration และ UAT ของ User Stories ที่เลือกส่งมอบผ่านเกณฑ์แล้ว ให้ผู้ประสานงานตรวจ candidate บน `integration/sprint1`:

1. ติดตั้งและเริ่มระบบได้ตาม README รวม Docker ตามข้อกำหนดส่งมอบ
2. UI, API และ SQL Server ทำงานร่วมกันใน flow ที่จะ Demo
3. เกณฑ์ DoD และผลทดสอบของงานที่ส่งมอบครบ โดยระบุผลจาก mock และระบบจริงแยกกัน
4. มีผลรับงานตามข้อตกลงกับ PO พร้อม Demo Script และคู่มือของเวอร์ชันนั้น
5. ตรวจ diff ของ candidate ว่ารวมเฉพาะงานที่ตกลงส่งมอบ และไม่มีฟีเจอร์ค้างที่ทำให้ flow ที่ Demo เสีย

ถ้ายังมีงานที่ส่งไม่ทันปะปนอยู่ ให้ทีมจัด candidate ให้ชัดและทดสอบใหม่ก่อนส่งมอบ
PR ที่เข้า `main` ใช้ **base: `main`**, **compare: `integration/sprint1`** พร้อมผล integration/UAT และรายการ User Stories ที่ส่งมอบ
เมื่อ review ผ่าน ให้ merge ด้วย Create a merge commit แล้วตรวจเวอร์ชันบน `main` อีกครั้ง

ขั้นรวมเวอร์ชันนี้แยกจาก PR ของแต่ละ task; ก่อนถึงจุดนี้ `main` ยังคงเป็นเวอร์ชัน Demo ก่อนหน้า
ในช่วงตั้งต้น repo ยังมีเพียง skeleton ให้ระบุสถานะนี้ตาม README จนกว่าจะผ่านเกณฑ์ Demo แรกจริง

## 9. เก็บเวอร์ชันด้วย tag

Tag ใช้ระบุ commit ที่ส่งมอบแน่นอน ส่วน `main` เดินต่อได้เมื่อมีเวอร์ชันใหม่
หลัง PR ส่งมอบ merge แล้ว ให้ผู้ประสานงานอัปเดต `main` ตรวจว่าเป็น commit ที่อนุมัติส่งมอบ และสร้าง annotated tag:

```powershell
git switch main
git pull --ff-only origin main
git log -1 --oneline
git tag -a v0.1.0 -m "Sprint 1 demo"
git push origin v0.1.0
```

`v0.1.0` และ `v0.2.0` เป็นตัวอย่างชื่อเวอร์ชันที่ทีมเลือกใช้สำหรับ Demo 1 และ Demo 2; ถ้ามี tag ชื่อนั้นแล้วให้เลือกชื่อใหม่
Tag เก็บจุดในประวัติ Git ส่วนข้อมูล SQL Server/config และวิธีเริ่มระบบที่ Demo ใช้ต้องมีคู่มือประกอบด้วย

ถ้าต้องการเปิดดูโค้ด Demo เดิมในเครื่องที่ working tree พร้อม:

```powershell
git fetch origin --tags
git switch --detach v0.1.0
```

คำสั่งนี้เป็น detached HEAD สำหรับดูหรือรันเวอร์ชันเดิม; ถ้าต้องแก้โค้ดให้สร้าง branch งานก่อน
เมื่อดูเสร็จและไม่มีงานค้าง ให้ `git switch main` เพื่อกลับไป branch หลัก

เริ่ม Sprint 2 โดยผู้ประสานงานสร้าง `integration/sprint2` จาก `main` ล่าสุดและ push แล้วให้สมาชิกใช้ขั้นตอนเดิม โดยเปลี่ยนชื่อ integration branch ให้ตรงรอบ

## เอกสารอ้างอิง

- [Conventional Commits: รูปแบบ type, scope และ description](https://www.conventionalcommits.org/en/v1.0.0/)
- [GitHub flow: branch, commit, Pull Request และ review](https://docs.github.com/en/get-started/using-github/github-flow)
- [Git pull และ --ff-only](https://git-scm.com/docs/git-pull)
- [Git merge และการแก้ conflict](https://git-scm.com/docs/git-merge)
- [Git workflows: topic branches และ integration branches](https://git-scm.com/docs/gitworkflows)
- [Git tag: เก็บจุดส่งมอบด้วย annotated tag](https://git-scm.com/docs/git-tag)
