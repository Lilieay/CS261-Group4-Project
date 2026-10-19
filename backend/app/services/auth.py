from __future__ import annotations

import secrets
from contextlib import AbstractContextManager
from dataclasses import dataclass
from time import monotonic
from typing import Callable

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import AUTH_SESSION_TTL_SECONDS
from app.dao.user_dao import UserDAO
from app.services.tu_api import TUAccount, TUVerificationError, verify_tu_account


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str
    display_name: str
    role: str


@dataclass(frozen=True)
class LoginSession:
    token: str
    user: AuthenticatedUser
    expires_at: float


class LoginRejected(Exception):
    """The account was not verified as an active student by TU."""


class AuthStorageUnavailable(Exception):
    """The verified user could not be stored in the application database."""


class AuthService:
    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        verify: Callable[[str, str], TUAccount | None] = verify_tu_account,
        *,
        session_ttl_seconds: int = AUTH_SESSION_TTL_SECONDS,
        clock: Callable[[], float] = monotonic,
    ):
        if session_ttl_seconds <= 0:
            raise ValueError("session_ttl_seconds must be positive")
        self._session_factory = session_factory
        self._verify = verify
        self._session_ttl_seconds = session_ttl_seconds
        self._clock = clock
        self._sessions: dict[str, LoginSession] = {}

    def login(self, username: str, password: str) -> LoginSession:
        normalized_username = username.strip()
        if not normalized_username or not password:
            raise LoginRejected

        try:
            account = self._verify(normalized_username, password)
        except TUVerificationError as error:
            raise LoginRejected from error

        if (
            account is None
            or not account.active
            or account.account_type.strip().lower() != "student"
        ):
            raise LoginRejected

        try:
            with self._session_factory() as session:
                try:
                    stored_user = UserDAO(session).get_or_create_from_tu_profile(
                        account.username.strip(),
                        displayname_en=account.display_name,
                    )
                    display_name = (
                        (stored_user.displayname_th or "").strip()
                        or (stored_user.displayname_en or "").strip()
                        or account.display_name.strip()
                        or stored_user.username
                    )
                    user = AuthenticatedUser(
                        id=stored_user.id,
                        username=stored_user.username,
                        display_name=display_name,
                        role="student",
                    )
                    session.commit()
                except SQLAlchemyError:
                    session.rollback()
                    raise
        except SQLAlchemyError as error:
            raise AuthStorageUnavailable from error

        token = secrets.token_urlsafe(32)
        now = self._clock()
        for expired_token, login_session in list(self._sessions.items()):
            if login_session.expires_at <= now:
                self._sessions.pop(expired_token, None)
        login_session = LoginSession(
            token=token, user=user, expires_at=now + self._session_ttl_seconds
        )
        self._sessions[token] = login_session
        return login_session

    def get_user(self, token: str) -> AuthenticatedUser | None:
        login_session = self._sessions.get(token)
        if login_session is None:
            return None
        if login_session.expires_at <= self._clock():
            self._sessions.pop(token, None)
            return None
        return login_session.user

    def logout(self, token: str) -> None:
        self._sessions.pop(token, None)
