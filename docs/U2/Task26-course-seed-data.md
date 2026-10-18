# Task26 course seed data

The catalog is based on Thammasat University's registrar course search at [vnweb68.reg.tu.ac.th/registrar/classinfo](https://vnweb68.reg.tu.ac.th/registrar/classinfo), reviewed 18 October 2026. The search used semester 1, academic year 2569, Rangsit, regular undergraduate classes, and curriculum 2566. Sections were collapsed by course code; the instructor list records distinct names shown across those sections. It describes instructors in the selected registrar results, not permanent course assignments.

The catalog contains 24 courses. CS301, CS303, CS403, and CS404 were excluded as project or co-operative education courses; the last three list 19 instructors each. Courses with more than two distinct listed instructors are excluded. CS263 is included because it appeared in the registrar results, although its section was closed. Inclusion does not imply current enrollment availability.

Names and instructor spellings preserve the registrar display. The [Task22 table design](task22-course-entity.md) and existing Course entity have one `instructor_name` column. One or two names are joined with comma and space, following Task22's example. Task21 mentions a second instructor field, but this seed does not change the Course schema. CS261 includes its registrar description. Descriptions not collected for other entries remain null.

The complete starting data is in [courses.json](../../backend/scripts/seed_data/datasets/courses.json). Each course and instructor list is formatted across separate lines for review.

`test` selects CS100, CS101, CS102, and CS261. `demo` selects all 24 entries. The data supports Task41's course prerequisites while keeping the test set small.

## Commands

Run from `backend` after installing `requirements.txt` and configuring `DB_CONNECTION_STRING` and `DB_PASSWORD` in `backend/.env` or the environment. The database must exist; create it with `db/init.sql` first. Create the product tables once with `python -m app.init_db` before seeding.

Run one action at a time:

```powershell
python -m scripts.seed_courses --dataset test --action seed
python -m scripts.seed_courses --dataset test --action check
python -m scripts.seed_courses --dataset test --action restore
python -m scripts.seed_courses --dataset demo --action seed
python -m scripts.seed_courses --dataset demo --action check
python -m scripts.seed_courses --dataset demo --action restore
```

For Docker Compose, run from the repository root. Set `MSSQL_SA_PASSWORD` privately in the root `.env`, start SQL Server, and create the development database using `db/init.sql` if it does not exist. Build the image and initialize product tables before using the packaged CLI:

```sh
docker compose build backend
docker compose up -d sqlserver
docker compose run --rm --no-deps backend python -m app.init_db
docker compose run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action seed
docker compose run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action check
docker compose run --rm --no-deps backend python -m scripts.seed_courses --dataset test --action restore
```

The CLI creates only the `course_seed_ownership` operational table, and only before `seed`. It does not create or alter product tables. Seed and restore run in a database transaction; reports print after commit. `check` does not create the ledger. Without a ledger, check can verify matching course data but cannot establish ownership, and restore preserves matching rows as unowned.

Only rows inserted by this tool are tracked. Matching preexisting rows are reused and never claimed. Supplied course names and instructors must match existing rows; a supplied description must also match. Uncollected null descriptions preserve existing values. Restore removes a tracked course only when its full recorded snapshot still matches and no guide references it. A shared test/demo claim is released while the other dataset remains active. Changed or referenced last-owner rows retain their ownership claim and include a reason in the report, so an operator can review and retry later. Database constraint failures abort the transaction.

Run seed/check/restore from one process at a time. The ledger and preflight protect normal repeated sequential runs; this tool does not coordinate concurrent seed/restore processes.

## Verification record

From `backend`, run focused SQLite tests with `python -m pytest test/test_course_seed_service.py`.

For the SQL Server variant in PowerShell, set `$env:TASK26_TEST_SQLSERVER = '1'` before running the same test command. The configured account must have permission to create test schemas. These tests roll back isolated temporary schemas. The missing-ledger case uses its own SQLite database in both modes.

The actual CLI writes to the configured development database. After verification, this workspace contains the 24-course demo dataset. See [actual verification results](Task26-verification-report.md).
