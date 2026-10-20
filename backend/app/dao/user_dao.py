from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User


class UserDAO:
    def __init__(self, session: Session):
        self.session = session
        
    def get_by_username(self, username: str) -> User | None:
        username = username.strip()
        
        statement = select(User).where(
            User.username == username
        )
        
        result = self.session.execute(statement)
        return result.scalar_one_or_none()
    
    def get_by_id(self, user_id: int) -> User | None:
        
        statement = select(User).where(
            User.id == user_id
        )
        
        result = self.session.execute(statement)
        return result.scalar_one_or_none()
    
    def get_or_create_from_tu_profile(
        self,
        username: str,
        displayname_th: str | None = None,
        displayname_en: str | None = None,
    ) -> User:
        username = username.strip()

        displayname_th = (displayname_th or "").strip() or None
        displayname_en = (displayname_en or "").strip() or None

        user = self.get_by_username(username)
        if user is None:
            try:
                with self.session.begin_nested():
                    user = User(
                        username=username,
                        displayname_th=displayname_th,
                        displayname_en=displayname_en,
                    )
                    self.session.add(user)
                    self.session.flush()
            except IntegrityError as error:
                if not self._is_duplicate_username(error):
                    raise
                user = self.get_by_username(username)
                if user is None:
                    raise

        if displayname_th is not None:
            user.displayname_th = displayname_th
        if displayname_en is not None:
            user.displayname_en = displayname_en

        self.session.flush()
        return user

    def _is_duplicate_username(self, error: IntegrityError) -> bool:
        message = str(error.orig)
        
        return (
            "(2627)" in message and "'uq_users_username'" in message
        )