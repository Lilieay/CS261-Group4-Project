from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db import SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
