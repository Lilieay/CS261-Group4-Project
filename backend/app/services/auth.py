from __future__ import annotations

import secrets
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Callable

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.dao.user_dao import UserDAO
from app.services.tu_api import TUAccount, TUVerificationError, verify_tu_account


@dataclass(frozen=True)
class User:
    id: int
    username: str
    display_name: str
    role: str


@dataclass(frozen=True)
class LoginSession:
    token: str
    user: User


class LoginRejected(Exception):
    """The account was not verified as an active student by TU."""


class AuthStorageUnavailable(Exception):
    """The verified user could not be stored in the application database."""


class AuthService:
    def __init__(
        self,
        session_factory: Callable[[], AbstractContextManager[Session]],
        verify: Callable[[str, str], TUAccount | None] = verify_tu_account,
    ):
        self._session_factory = session_factory
        self._verify = verify
        self._sessions: dict[str, User] = {}

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
                user = User(
                    id=stored_user.id,
                    username=stored_user.username,
                    display_name=display_name,
                    role="student",
                )
        except SQLAlchemyError as error:
            raise AuthStorageUnavailable from error

        token = secrets.token_urlsafe(32)
        self._sessions[token] = user
        return LoginSession(token=token, user=user)

    def get_user(self, token: str) -> User | None:
        return self._sessions.get(token)

    def logout(self, token: str) -> None:
        self._sessions.pop(token, None)
