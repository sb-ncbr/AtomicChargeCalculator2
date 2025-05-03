from db.schemas.user import User
from db.database import SessionManager

from sqlalchemy import select


class UserRepository:
    """Repository for managing calculation sets."""

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def get(self, openid: str) -> User | None:
        """Get user by their openid.

        Args:
            openid (str): Openid of the user.

        Returns:
            User | None: User with provided openid if exists, otherwise None.
        """

        statement = select(User).where(User.openid == openid)

        with self.session_manager.session() as session:
            user = (session.execute(statement)).scalars().first()
            return user

    def store(self, user: User) -> User:
        """Store user in the database.

        Args:
            user (User): User to store.

        Returns:
            User: Stored user.
        """

        with self.session_manager.session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
