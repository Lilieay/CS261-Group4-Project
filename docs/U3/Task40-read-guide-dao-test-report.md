# Task40: Read Guide DAO test report

## Test setup

The same seven automated DAO tests passed on SQL Server and on an in-memory SQLite database. SQL Server tests use the application's configured connection with its existing encryption and authentication settings.

Fixture data has two courses and one publisher. CS261 has two guides (2568/semester 1/midterm and 2567/semester 2/final); CS102 has one guide matching the first CS261 guide's filter values. The first guide contains a Thai title and multiline Thai topics, with nullable counts and advice. The filter-values test adds another CS261 guide with duplicate filter values.

Each SQL Server test creates a unique `task40_test_<uuid>` schema and its tables inside an outer transaction. The Session uses `join_transaction_mode="rollback_only"`, so fixture commits do not commit that outer transaction. Cleanup closes the Session, rolls back the outer transaction, and checks `sys.schemas` to confirm the test schema no longer exists. Cleanup also runs when a test fails. Existing application tables and rows are not changed. SQLite databases are discarded after each test.

## Results

| ID | Case / input | Expected result | Actual result on SQL Server | Status |
|---|---|---|---|---|
| T40-DAO01 | CS261, 2568, semester 1, midterm | One guide matching all filters; Course and Publisher already loaded | One matching CS261 guide; relationships readable after detaching the results from the Session | Pass |
| T40-DAO02 | CS261 with no filters, then each of the three filters separately | Both CS261 guides without filters; only the first guide for each single filter | Exact guide IDs returned in each case | Pass |
| T40-DAO03 | CS261, year 2500 | Empty list | Empty list | Pass |
| T40-DAO04 | CS261, year 2568, with matching data in CS102 | Only CS261 data | Only CS261 guide returned | Pass |
| T40-DAO05 | Existing guide ID, then missing ID -1 | Guide with relationships, Thai text, newlines and NULL values preserved; missing ID returns `None` | All checked values matched; missing ID returned `None` | Pass |
| T40-DAO06 | Filter values for CS261 and CS102, including a duplicate within CS261 | Distinct sorted values scoped to each course | CS261: years [2567, 2568], semesters [1, 2], periods [final, midterm]; CS102: [2568], [1], [midterm] | Pass |
| T40-DAO07 | Course without guides | Three empty filter lists | Three empty lists | Pass |

Run from `backend` for SQLite:

```powershell
$env:PYTHONPATH='.'
Remove-Item Env:TASK40_TEST_SQLSERVER -ErrorAction SilentlyContinue
.venv\Scripts\python.exe -m unittest discover -s test -p test_read_guide_dao.py -v
```

Run from `backend` for SQL Server in a process that can access the configured Windows credentials:

```powershell
$env:PYTHONPATH='.'
$env:TASK40_TEST_SQLSERVER='1'
.venv\Scripts\python.exe -m unittest discover -s test -p test_read_guide_dao.py -v
```

Captured runner results:

```text
SQLite:     Ran 7 tests in 0.184s — OK
SQL Server: Ran 7 tests in 1.246s — OK
```

The SQL Server run included successful schema-rollback checks after all seven cases.

The SQL Server DDL was also compiled with SQLAlchemy's MSSQL dialect. It produced `SMALLINT` for `academic_year`, `TINYINT` for `semester`, the specified `NVARCHAR` lengths, identity primary key, and both foreign keys.

## Connection diagnosis

The initial failure occurred in the agent's sandbox. ODBC Driver 18 reported SQLSTATE `08001`, encryption unsupported, and SSL provider error `-2146893042` (no credentials available). The SQL Server service was running.

| Experiment | Change | Result / conclusion |
|---|---|---|
| Reproduce | Execute `SELECT 1` with the configured SQLAlchemy connection inside the sandbox | Same ODBC/SSL failure; the failure occurs before DAO queries |
| Execution-context comparison | Repeat the identical command outside the sandbox | `SELECT 1` passed; the restricted execution context caused the failure |
| DAO integration | Run the seven tests outside the sandbox against SQL Server | All passed, including schema creation, fixture inserts, reads and cleanup |
| SQLite check | Run the same suite inside the sandbox against SQLite | All seven passed |

No connection-string, encryption, certificate-trust, authentication or SQL Server service setting needed to change. For this agent session, SQL Server commands require execution outside the sandbox.
