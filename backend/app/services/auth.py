import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str
    password: str
    display_name: str
    role: str


USERS = {
    "student": User(1, "student", "password123", "Student User", "student"),
    "admin": User(2, "admin", "admin123", "Administrator", "admin"),
}

# In-memory session สำหรับการสาธิตและการทดสอบ
ACTIVE_SESSIONS: dict[str, User] = {}


def authenticate(username: str, password: str) -> User | None:
    user = USERS.get(username)
    if user is None or not secrets.compare_digest(user.password, password):
        return None
    return user


def create_session(user: User) -> str:
    token = secrets.token_urlsafe(32)
    ACTIVE_SESSIONS[token] = user
    return token


def get_user_by_token(token: str) -> User | None:
    return ACTIVE_SESSIONS.get(token)


def delete_session(token: str) -> None:
    ACTIVE_SESSIONS.pop(token, None)
