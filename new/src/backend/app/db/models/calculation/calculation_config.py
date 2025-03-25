import uuid
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.models import Base


class CalculationConfig(Base):
    """Calculation config database model. It represents a single calculation configuration."""

    __tablename__ = "calculation_configs"

    id: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    method: Mapped[str] = mapped_column(sa.VARCHAR(20), nullable=False)
    parameters: Mapped[str | None] = mapped_column(sa.VARCHAR(50), nullable=True)
    read_hetatm: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    ignore_water: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    permissive_types: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)

    set_id: Mapped[str] = mapped_column(
        sa.Uuid, sa.ForeignKey("calculation_sets.id"), nullable=False
    )

    calculation_set = relationship("CalculationSet", back_populates="configs")
    calculations = relationship(
        "Calculation", back_populates="config", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"""<CalculationConfig
        id={self.id}
        method={self.method}
        parameters={self.parameters}
        read_hetatm={self.read_hetatm}
        ignore_water={self.ignore_water}
        permissive_types={self.permissive_types}>"""

    def __eq__(self, other):
        return (
            self.method == other.method
            and self.parameters == other.parameters
            and self.read_hetatm == other.read_hetatm
            and self.ignore_water == other.ignore_water
            and self.permissive_types == other.permissive_types
            and self.set_id == other.set_id
        )
