# Task16 Backend/Docker Verification

## Scope

This report covers backend login persistence and Docker database bootstrap.
The UI-to-API and end-to-end login checks depend on the Task14 frontend work
and are not reported as complete here.

Code branch: `feat/task16-backend-docker`.
Verified code revision: `e9bde9632318c4363c64b1b0aacf0cc7c1b55a71`.
Environment: Windows PowerShell, Python 3.14, Docker Compose, SQL Server 2022.

## Automated checks

| Check | Environment | Expected result | Actual result |
|---|---|---|---|
| Auth API success, status, `/me`, and logout | Local Python 3.14, SQLite test database, injected TU verifier | User is persisted, token works, logout revokes token | PASS |
| Repeated and rejected login | Local Python 3.14, SQLite test database | Same username reuses its ID; rejected account creates no user | PASS |
| Database failure | Local Python 3.14, injected SQLAlchemy failure | Login returns 503 and issues no token | PASS |
| Guide list, update, and delete authorization | Local Python 3.14, SQLite test database with injected auth service | Existing authenticated API behavior remains intact | PASS |
| Full backend pytest suite | Local Python 3.14 | Existing and Task16 backend tests pass | 58 passed, 7 subtests passed |
| SQL Server login persistence | Temporary Docker verification script, removed after use | Repeat login reuses the persisted user ID | 1 passed; verification script is not included in this delivery |

## Docker checks

| Check | Expected result | Actual result |
|---|---|---|
| Compose configuration | Configuration resolves without printing secrets | PASS (`docker compose config --quiet`) |
| Repeated backend bootstrap | Database and tables remain available; existing data is retained | PASS (PowerShell script exited 0 against the existing SQL Server volume) |
| SQL Server persistence test | A unique temporary username is inserted, reused, and removed | PASS (1 test) |
| Login through backend API | Verified demo student receives a persisted database user ID | PASS |
| Backend restart | Old in-memory token is rejected and next login returns the same database user ID | PASS |

## Limits

Verification used the local mock TU provider. The real TU endpoint was not
tested. Task14 frontend changes are still owned by the frontend task owner, so
UI-to-API and full end-to-end Task16 evidence remain pending.

Record the commit SHA, command, environment, result, and sanitized evidence
after each check. Never include `.env`, passwords, or access tokens.
