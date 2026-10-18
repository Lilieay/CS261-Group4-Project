# Task26 verification results

Date: 18 October 2026. Branch: `feat/task26-course-seed`, based directly on `integration/sprint1` at `228a6f8`.

Verified implementation revision: `ebf07d1`. Data: `924ce8b`; seed service: `9d7f139`; Docker packaging: `ecccaa5`; tests: `ebf07d1`.

## Environment and data

Windows PowerShell, local Python 3.14 environment, Docker Desktop 29.8.2, and SQL Server 2022 Developer in Docker Compose. Credentials stay in ignored environment files.

The registrar source was read through the user's open Chrome session at [TU course search](https://vnweb68.reg.tu.ac.th/registrar/classinfo). Both result pages contained 67 section/curriculum rows. Filtering to curriculum 2566 and applying the documented instructor and course exclusions produced 24 distinct courses. No account identifiers or session data were saved.

Before CLI verification: courses = 0, guides = 0, users = 1. After verification: courses = 24, guides = 0, users = 1, demo ownership records = 24.

## Observed results

| ID | Input and expected behavior | Observed result | Status |
|---|---|---|---|
| T26-DATA | Real registrar names; one or two distinct instructors; exclude project/co-op courses | 24 entries; CS301, CS303, CS403, CS404 absent; CS261 has its real Thai description | PASS |
| T26-UNIT | Course seed and existing Task41 seed behavior under SQLite | 20 tests and 4 subtests passed | PASS |
| T26-SQL | Same suites with isolated SQL Server schema mode enabled | 20 tests and 4 subtests passed; no temporary schemas remained | PASS |
| T26-CLI-01 | Seed test dataset, check it, then seed again | First run inserted 4; check matched 4; repeat reused 4 with no new rows | PASS |
| T26-CLI-02 | Restore test dataset twice | First run removed 4; second run removed 0 | PASS |
| T26-CLI-03 | Seed and check demo dataset in separate processes | Inserted 24 and matched all 24 | PASS |
| T26-DAO | Fresh process calls `CourseDAO.search('cs261')` and `get_by_id` | Exactly one CS261 returned; Thai instructor and description matched the dataset | PASS |
| T26-SAFE | Preserve unrelated data and caller transaction boundaries | Existing user count stayed 1; changed, unowned, referenced, shared, and caller-rollback cases passed | PASS |
| T26-IMPORT | Configure ORM mappers in a fresh interpreter | Regression test and real Docker process passed after registering the User relationship target | PASS |

## Reproduce

From `backend`, the SQLite run was:

```powershell
python -m pytest -p no:cacheprovider test/test_course_seed_service.py test/test_guide_seed_service.py -q
```

From the repository root, the SQL Server run was:

```powershell
$task26Tests = (Resolve-Path backend/test).Path
docker compose run --rm --no-deps -e TASK26_TEST_SQLSERVER=1 -e TASK41_TEST_SQLSERVER=1 -v "${task26Tests}:/task26-tests:ro" backend python -m pytest -p no:cacheprovider /task26-tests/test_course_seed_service.py /task26-tests/test_guide_seed_service.py -q
```

Each suite uses its own temporary SQL Server schemas and rolls them back. Data parsing, import, and missing-ledger checks do not all access SQL Server; the missing-ledger case explicitly creates SQLite. The real CLI runs in T26-CLI-01 through T26-CLI-03 separately verify durable data in the development database.

The first real CLI run exposed a missing `User` mapper registration that in-process tests had hidden by importing User themselves. A fresh-interpreter regression now covers the failing boundary. Its working directory comes from the installed service module so the test also works when mounted into Docker separately.

## Delivery limits

Task26 does not require Task28 or the unmerged Task16 branch. It seeds database data only; the current frontend preview is not connected to these rows. No Course API, frontend integration, or registrar synchronization is claimed. Course instructors are a snapshot for the selected semester. Course descriptions other than CS261 were not collected.

Seed and restore support one process at a time. The tool checks Guide references and relies on database constraints to roll back other restrictive foreign-key failures. The operational ownership table is an addition; product table definitions are unchanged.

No merge or push has been performed. Push requires the user's explicit authorization. The temporary implementation plan is excluded from commits and removed before delivery.
