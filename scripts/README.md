# Shared development scripts

Use this directory for repository-level development commands. Name scripts by
their purpose so tasks can reuse them.

## Start the backend and database

From the repository root, configure `.env` using `.env.example`, then run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1
```

The script builds the backend, waits for SQL Server, creates the database and
missing tables, then starts and checks the backend. Existing data is retained.

Backend seed commands remain under `backend/scripts/` alongside their Python
services and datasets. See the corresponding seed documentation for usage.
