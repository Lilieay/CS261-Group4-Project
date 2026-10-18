"""TU account verification adapter.

Production uses the endpoint configured by TU_API_URL. The mock provider is
available only for local tests/demo and is never treated as a real TU result.
"""

import json
import http.client
import math
import os
import secrets
from dataclasses import dataclass
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
    application_key = os.getenv("TU_API_KEY", "").strip()
    if not endpoint or not application_key:
        raise TUVerificationError(
            "TU_API_URL and TU_API_KEY must be configured for real TU API"
        )

    try:
        timeout = float(os.getenv("TU_API_TIMEOUT", "5"))
    except ValueError as error:
        raise TUVerificationError("TU_API_TIMEOUT must be a positive number") from error
    if not math.isfinite(timeout) or timeout <= 0:
        raise TUVerificationError("TU_API_TIMEOUT must be a positive number")

    try:
        payload = json.dumps({"UserName": username, "PassWord": password}).encode("utf-8")
        request = Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Application-Key": application_key,
            },
            method="POST",
        )
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise TUVerificationError("TU API rejected the request")
            body = json.loads(response.read().decode("utf-8"))
    except (http.client.HTTPException, OSError, ValueError) as error:
        raise TUVerificationError("TU API is unavailable or returned invalid data") from error

    if not isinstance(body, dict):
        raise TUVerificationError("TU API returned an invalid response shape")

    # TU's Authentication API returns status/type/display names. Treat only
    # an explicit successful student response as an eligible account.
    if body.get("status") is not True:
        return None
    raw_type = body.get("type")
    if not isinstance(raw_type, str) or raw_type.strip().lower() != "student":
        return None
    display_name = ""
    for field in ("displayname_th", "displayname_en"):
        value = body.get(field)
        if isinstance(value, str) and value.strip():
            display_name = value.strip()
            break
    normalized_username = username.strip()
    if not normalized_username or not display_name:
        return None
    return TUAccount(normalized_username, display_name, "student", True)


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

