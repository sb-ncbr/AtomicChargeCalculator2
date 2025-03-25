"""This module provides a repository for calculation configs."""

from sqlalchemy import select
from sqlalchemy.orm import joinedload


from db.database import SessionManager
from db.models.calculation.calculation_config import CalculationConfig
from db.models.moleculeset_stats import MoleculeSetStats


class MoleculeSetStatsRepository:
    """Repository for managing MoleculeSetStats."""

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def get(self, file_hash: str) -> MoleculeSetStats | None:
        """Get info about a file based on file hash.

        Args:
            file_hash (str): Hash of the file.

        Returns:
            MoleculeSetStats | None: Information about the file or None if not found.
        """

        statement = (
            select(MoleculeSetStats)
            .options(joinedload(MoleculeSetStats.atom_type_counts))
            .execution_options(populate_existing=True)
            .where(MoleculeSetStats.file_hash == file_hash)
        )

        with self.session_manager.session() as session:
            info = (session.execute(statement)).scalars().first()

            return info

    def store(self, info: MoleculeSetStats) -> CalculationConfig:
        """Store info about a file in the database.
           If a given config already exists, it is returned.

        Args:
            config (CalculationConfig): Calculation config.

        Raises:
            ValueError: If the calculation set to which the calculation config belongs is not found.

        Returns:
            CalculationConfig: Stored calculation config.
        """

        exists = self.get(info.file_hash)

        if exists is not None:
            return exists

        with self.session_manager.session() as session:
            session.add(info)
            session.commit()
            session.refresh(info)
            return info
