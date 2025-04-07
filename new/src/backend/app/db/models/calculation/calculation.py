import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.models import Base

from integrations.chargefw2.base import Charges


class Calculation(Base):
    """Calculation database model. It represents a single calculation (single config and file)."""

    __tablename__ = "calculations"

    id: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    file: Mapped[str] = mapped_column(sa.VARCHAR(100), nullable=False)
    file_hash: Mapped[str] = mapped_column(
        sa.VARCHAR(100), sa.ForeignKey("molecule_set_stats.file_hash"), nullable=False
    )
    charges: Mapped[Charges] = mapped_column(sa.JSON, nullable=False)

    set_id: Mapped[str] = mapped_column(
        sa.Uuid, sa.ForeignKey("calculation_sets.id"), nullable=False
    )
    config_id: Mapped[str] = mapped_column(
        sa.Uuid, sa.ForeignKey("calculation_configs.id"), nullable=False
    )

    calculation_set = relationship("CalculationSet", back_populates="calculations")
    config = relationship("CalculationConfig", back_populates="calculations")
    info = relationship("MoleculeSetStats", foreign_keys=[file_hash], uselist=False)

    def __repr__(self):
        return f"""<Calculation
        id={self.id}
        hash={self.set_id}
        file={self.file}
        file_hash={self.file_hash}
        set_id={self.set_id}
        config_id={self.config_id}>"""
