"""Database connection manager."""

from contextlib import contextmanager
from sqlalchemy.orm import Session, sessionmaker, scoped_session

from sqlalchemy import create_engine


class Database:
    """Database connection and model manager."""

    def __init__(self, db_url: str):
        self._engine = create_engine(db_url, future=True, pool_size=20, max_overflow=10)
        self.session_factory = scoped_session(
            sessionmaker(
                bind=self._engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
        )


class SessionManager:
    """Database session manager."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    @contextmanager
    def session(self):
        """Provide a transactional scope."""

        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
