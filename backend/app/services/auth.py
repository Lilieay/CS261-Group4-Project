import secrets
from dataclasses import dataclass

from app.services.tu_api import TUVerificationError, verify_tu_account


@dataclass(frozen=True)
class User:
    id: int
    username: str
    display_name: str
    role: str


USERS = {
    "student": User(1, "student", "Student User", "student"),
}

# In-memory session สำหรับการสาธิตและการทดสอบ
ACTIVE_SESSIONS: dict[str, User] = {}


def authenticate(username: str, password: str) -> User | None:
    normalized_username = username.strip()
    if not normalized_username or not password:
        return None
    try:
        account = verify_tu_account(normalized_username, password)
    except TUVerificationError:
        # Fail closed when TU cannot verify the account.
        return None
    if account is None or account.account_type != "student" or not account.active:
        return None

    # Demo storage is keyed by the verified TU username. No TU password is
    # stored in the internal User/profile object.
    user = USERS.get(account.username)
    if user is None:
        user = User(len(USERS) + 1, account.username, account.display_name, "student")
        USERS[account.username] = user
    return user


def create_session(user: User) -> str:
    token = secrets.token_urlsafe(32)
    ACTIVE_SESSIONS[token] = user
    return token


def get_user_by_token(token: str) -> User | None:
    return ACTIVE_SESSIONS.get(token)


def delete_session(token: str) -> None:
    ACTIVE_SESSIONS.pop(token, None)

