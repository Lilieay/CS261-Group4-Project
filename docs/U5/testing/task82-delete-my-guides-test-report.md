# Task82: Delete My Guides

## Scope

The shared-courses page now lets the signed-in publisher delete an owned guide through the existing DELETE /api/my-guides/{guide_id} API. The UI shows the guide title and course in a confirmation dialog, then reloads the owned-guide list after the request. The backend ownership check and DAO were already present, so this task adds no backend schema or authorization changes.

## Verification

| Check | Result |
|---|---|
| Frontend unit tests (npm.cmd test from frontend) | 47 passed |
| Backend deletion API and DAO tests (python -m pytest test/test_my_guide_deletions_api.py test/test_delete_owned_guide_dao.py -q from backend) | 13 passed |
| Browser cancel check | Cancel closed the confirmation dialog; the disposable record remained visible |
| Browser confirmed delete | The disposable record disappeared from the list and the page showed the success status |
| SQL Server verification | Disposable record ID 8 was absent; existing owned guide IDs 5, 6, and 7 remained; total returned to 7 |
| git diff --check | Passed |

The browser check used the isolated Task60 Docker stack and its mock login. The disposable record was created through the local publish API specifically for this check, then removed through the page. No production account or database was used.

## Behavior and failure handling

- The frontend proxy accepts only a positive SQL integer ID and pins the upstream path to /api/my-guides/{id}.
- It forwards the bearer token, disables caching, preserves backend status and response bodies, and returns 502 if the backend cannot be reached.
- The browser client validates that the success response identifies the requested guide.
- The UI prevents another delete request while one is pending. Canceling or closing the dialog does not call the API.
- On 404 or an uncertain network/server result, the UI reloads the owned-guide list and tells the user to check it before retrying.

## Files changed

- frontend/src/server.js and frontend/src/server.test.js: fixed-path DELETE proxy and coverage.
- frontend/public/js/guide-api.js and frontend/src/guide-api.test.js: authenticated delete client and response validation.
- frontend/public/js/shared-courses.js, frontend/public/shared-courses.html, and frontend/src/shared-courses.test.js: confirmation dialog, delete action, refresh, and UI coverage.
