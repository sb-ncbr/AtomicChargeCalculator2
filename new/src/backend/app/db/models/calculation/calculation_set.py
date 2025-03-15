import uuid
import sqlalchemy as sa

from datetime import datetime

from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.models import Base


class CalculationSet(Base):
    """Calculation set database model. It is a collection of calculations."""

    __tablename__ = "calculation_sets"

    id: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=sa.func.timezone("UTC", sa.func.current_timestamp()),
    )
    user_id: Mapped[str] = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="calculation_sets")
    calculations = relationship(
        "Calculation", back_populates="calculation_set", cascade="all, delete-orphan"
    )
    configs = relationship(
        "CalculationConfig", back_populates="calculation_set", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<CalculationSet id={self.id}>"
