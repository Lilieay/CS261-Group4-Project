# Task16 Backend/Docker Runbook

## Start the backend

1. Copy `.env.example` to `.env` in the repository root.
2. Set a private `MSSQL_SA_PASSWORD` in `.env`. Keep that file untracked.
3. Run this command from the repository root in PowerShell:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/task16/start.ps1
   ```

The script builds the backend image, starts SQL Server, waits for its existing
Compose health check, runs `db/init.sql`, creates missing ORM tables, starts
the backend, and checks its existing root route. The SQL Server named volume
is retained. Running setup again does not drop the database or its data.

Open the backend API docs at <http://127.0.0.1:8000/docs>.

## TU verification mode

`TU_API_MODE=mock` is for local development and automated tests. It does not
verify a real university account. Use `TU_API_MODE=real` and configure
`TU_API_URL` only with the authorized TU endpoint and test account. Do not
include real passwords or tokens in reports.

## Database behavior

`db/init.sql` creates `CS261Group4Dev` only when it does not exist.
`python -m app.init_db` creates missing ORM tables and keeps existing rows.
It is not a schema migration tool.

After TU verifies an active student, Login finds or creates the application
user through `UserDAO`. The API token remains in memory and is cleared when
the backend process restarts.
