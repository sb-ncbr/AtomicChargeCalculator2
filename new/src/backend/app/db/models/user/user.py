import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.models import Base


class User(Base):
    """User model. It only stores openid of the user."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    openid: Mapped[str] = mapped_column(sa.VARCHAR(100), nullable=False)

    calculation_sets = relationship(
        "CalculationSet", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id}, openid={self.openid}>"
