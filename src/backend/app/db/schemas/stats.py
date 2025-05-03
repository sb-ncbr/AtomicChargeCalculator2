import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.schemas import Base


class AtomTypeCount(Base):
    """Atom type count database model."""

    __tablename__ = "atom_type_counts"

    id: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(sa.VARCHAR(10), primary_key=False)
    count: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    molecule_set_id = mapped_column(
        sa.VARCHAR(100), sa.ForeignKey("molecule_set_stats.file_hash"), nullable=False
    )
    molecule_set_stats = relationship("MoleculeSetStats", back_populates="atom_type_counts")

    def __repr__(self):
        return f"""<AtomTypeCount id={self.id}, symbol={self.symbol}, count={self.count}, molecule_set_id={self.molecule_set_id}"""


class MoleculeSetStats(Base):
    """
    Molecule set stats database model.
    Holds information about the molecules in the provided file.
    Files are identified by their file_hash.
    """

    __tablename__ = "molecule_set_stats"

    file_hash: Mapped[str] = mapped_column(sa.VARCHAR(100), primary_key=True)
    total_molecules: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    total_atoms: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    atom_type_counts = relationship("AtomTypeCount", back_populates="molecule_set_stats")
    calculation_sets = relationship(
        "CalculationSet",
        secondary="calculation_set_stats",
        back_populates="molecule_set_stats",
        viewonly=True,
    )
    calculation_set_associations = relationship(
        "CalculationSetStats", back_populates="molecule_set"
    )

    def __repr__(self):
        return f"""<MoleculeSetStats file_hash={self.file_hash}, total_molecules={self.total_molecules}, total_atoms={self.total_atoms}, atom_type_counts={self.atom_type_counts}"""
