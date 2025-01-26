"""Calculation database models."""

import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped
from sqlalchemy.dialects.postgresql import JSON
from db.database import Base


class Calculation(Base):
    """Calculation database model."""

    __tablename__ = "calculations"

    id: Mapped[str] = sa.Column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    file_hash: Mapped[str] = sa.Column(sa.Text, nullable=False)
    method: Mapped[str] = sa.Column(sa.VARCHAR(20), nullable=False)
    parameters: Mapped[str] = sa.Column(sa.VARCHAR(50), nullable=True)
    read_hetatm: Mapped[bool] = sa.Column(sa.Boolean, nullable=False)
    ignore_water: Mapped[bool] = sa.Column(sa.Boolean, nullable=False)
    charges: Mapped[dict] = sa.Column(JSON, nullable=False)
    sa.UniqueConstraint(file_hash, method, parameters, read_hetatm, ignore_water)

    def __repr__(self):
        return f"""<Calculation
        id={self.id}
        hash={self.file_hash}
        method={self.method}
        parameters={self.parameters}
        read_hetatm={self.read_hetatm}
        ignore_water={self.ignore_water}
        charges={self.charges}>"""
