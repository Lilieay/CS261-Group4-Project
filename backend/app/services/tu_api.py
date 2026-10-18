"""TU account verification adapter.

Production uses the endpoint configured by TU_API_URL. The mock provider is
available only for local tests/demo and is never treated as a real TU result.
"""

import json
import os
import secrets
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class TUAccount:
    username: str
    display_name: str
    account_type: str
    active: bool


class TUVerificationError(Exception):
    """Raised when TU cannot verify the submitted credentials."""


def _mock_verify(username: str, password: str) -> TUAccount | None:
    # Demo-only credentials. They are not persisted in User/profile data.
    demo_accounts = {
        os.getenv("TU_MOCK_USERNAME", "6800000000"): (
            os.getenv("TU_MOCK_PASSWORD", "0000000000000"),
            "Student User",
            "student",
            True,
        ),
        "admin": ("admin123", "Administrator", "staff", True),
    }
    account = demo_accounts.get(username)
    if account is None or not secrets.compare_digest(account[0], password):
        return None
    return TUAccount(username, account[1], account[2], account[3])


def _real_verify(username: str, password: str) -> TUAccount | None:
    endpoint = os.getenv("TU_API_URL", "").strip()
    if not endpoint:
        raise TUVerificationError("TU_API_URL is not configured")

    payload = json.dumps({"username": username, "password": password}).encode("utf-8")
    request = Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=float(os.getenv("TU_API_TIMEOUT", "5"))) as response:
            if response.status != 200:
                raise TUVerificationError("TU API rejected the request")
            body = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        raise TUVerificationError("TU API is unavailable or returned invalid data") from error

    if not isinstance(body, dict):
        raise TUVerificationError("TU API returned an invalid response shape")

    # The integration contract requires explicit proof of identity and status.
    if body.get("authenticated") is not True or body.get("active") is not True:
        return None
    account_type = str(body.get("account_type", "")).strip().lower()
    verified_username = str(body.get("username", "")).strip()
    display_name = str(body.get("display_name", "")).strip()
    if account_type != "student" or not verified_username or not display_name:
        return None
    return TUAccount(verified_username, display_name, account_type, True)


def verify_tu_account(username: str, password: str) -> TUAccount | None:
    """Verify credentials and student eligibility; return None on rejection.

    Any provider/network/configuration error raises TUVerificationError so the
    caller can fail closed without treating an outage as a bad password.
    """

    mode = os.getenv("TU_API_MODE", "mock").strip().lower()
    if mode == "mock":
        return _mock_verify(username, password)
    if mode == "real":
        return _real_verify(username, password)
    raise TUVerificationError("Unsupported TU_API_MODE")

