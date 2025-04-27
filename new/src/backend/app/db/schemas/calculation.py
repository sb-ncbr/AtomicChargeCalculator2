import uuid

from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.schemas import Base


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
    advanced_settings_id: Mapped[str] = mapped_column(
        sa.Uuid, sa.ForeignKey("advanced_settings.id"), nullable=False
    )

    user = relationship("User", back_populates="calculation_sets")
    configs = relationship(
        "CalculationConfig", secondary="calculation_set_configs", back_populates="calculation_sets"
    )
    advanced_settings = relationship("AdvancedSettings", back_populates="calculation_sets")
    molecule_set_stats = relationship(
        "MoleculeSetStats",
        secondary="calculation_set_stats",
        back_populates="calculation_sets",
        viewonly=True,
    )
    molecule_set_stats_associations = relationship(
        "CalculationSetStats", back_populates="calculation_set", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CalculationSet id={self.id}, created_at={self.created_at}>"


class CalculationSetConfig(Base):
    """M:N relationship table between CalculationSet and CalculationConfig"""

    __tablename__ = "calculation_set_configs"

    calculation_set_id: Mapped[str] = mapped_column(
        sa.Uuid, sa.ForeignKey("calculation_sets.id"), nullable=False, primary_key=True
    )
    config_id: Mapped[str] = mapped_column(
        sa.Uuid, sa.ForeignKey("calculation_configs.id"), nullable=False, primary_key=True
    )

    def __repr__(self) -> str:
        return f"<CalculationSetConfig calculation_set_id={self.calculation_set_id}, config_id={self.config_id}>"

    __table_args__ = (sa.UniqueConstraint("calculation_set_id", "config_id"),)


class CalculationConfig(Base):
    """Calculation config database model. It represents a single calculation configuration."""

    __tablename__ = "calculation_configs"

    id: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    method: Mapped[str] = mapped_column(sa.VARCHAR(20), nullable=False)
    parameters: Mapped[str | None] = mapped_column(sa.VARCHAR(50), nullable=True)

    calculation_sets = relationship(
        "CalculationSet", secondary="calculation_set_configs", back_populates="configs"
    )
    calculations = relationship("Calculation", back_populates="config")

    def __repr__(self) -> str:
        return (
            f"<CalculationConfig id={self.id}, method={self.method}, parameters={self.parameters}>"
        )

    __table_args__ = (sa.UniqueConstraint("method", "parameters"),)

    def __eq__(self, other):
        return self.method == other.method and self.parameters == other.parameters


class CalculationSetStats(Base):
    """M:N relationship table between CalculationSet and MoleculeSetStats"""

    __tablename__ = "calculation_set_stats"

    calculation_set_id: Mapped[str] = mapped_column(
        sa.Uuid, sa.ForeignKey("calculation_sets.id"), primary_key=True
    )
    molecule_set_id: Mapped[str] = mapped_column(
        sa.VARCHAR(100), sa.ForeignKey("molecule_set_stats.file_hash"), primary_key=True
    )

    file_name: Mapped[str] = mapped_column(sa.VARCHAR(255), nullable=True)

    calculation_set = relationship(
        "CalculationSet", back_populates="molecule_set_stats_associations"
    )
    molecule_set = relationship("MoleculeSetStats", back_populates="calculation_set_associations")

    def __repr__(self) -> str:
        return f"<CalculationSetStats calculation_set_id={self.calculation_set_id}, molecule_set_id={self.molecule_set_id}>"

    __table_args__ = (sa.UniqueConstraint("calculation_set_id", "molecule_set_id"),)


class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    file_name: Mapped[str] = mapped_column(sa.VARCHAR(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(sa.VARCHAR(100), nullable=False)
    charges: Mapped[dict] = mapped_column(sa.JSON, nullable=False)

    config_id: Mapped[str] = mapped_column(
        sa.Uuid, sa.ForeignKey("calculation_configs.id"), nullable=False
    )
    advanced_settings_id: Mapped[str] = mapped_column(
        sa.Uuid, sa.ForeignKey("advanced_settings.id"), nullable=False
    )

    config = relationship("CalculationConfig", back_populates="calculations")
    advanced_settings = relationship("AdvancedSettings", back_populates="calculations")

    def __repr__(self) -> str:
        return f"<Calculation id={self.id}, file_name={self.file_name}, file_hash={self.file_hash}>"


class AdvancedSettings(Base):
    __tablename__ = "advanced_settings"

    id: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    read_hetatm: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    ignore_water: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    permissive_types: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)

    calculation_sets = relationship("CalculationSet", back_populates="advanced_settings")
    calculations = relationship("Calculation", back_populates="advanced_settings")

    def __repr__(self):
        return f"""<AdvancedSettings id={self.id}, read_hetatm={self.read_hetatm}, ignore_water={self.ignore_water}, permissive_types={self.permissive_types}"""

    __table_args__ = (sa.UniqueConstraint("read_hetatm", "ignore_water", "permissive_types"),)
