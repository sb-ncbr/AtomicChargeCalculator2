"""This module provides a repository for calculation configs."""

from sqlalchemy import and_, select


from db.database import SessionManager
from db.models.calculation.calculation_config import CalculationConfig
from db.repositories.calculation_set_repository import CalculationSetRepository


class CalculationConfigRepository:
    """Repository for managing calculation configs."""

    def __init__(
        self,
        session_manager: SessionManager,
        set_repository: CalculationSetRepository,
    ):
        self.session_manager = session_manager
        self.set_repository = set_repository

    def get_all(self, calculation_set_id: str) -> list[CalculationConfig]:
        """Get all calculation configs for given calculation set.

        Args:
            calculation_set_id (str): Id of the calculation set.

        Returns:
            list[CalculationConfig]: List of calculation configs.
        """

        statement = select(CalculationConfig).where(CalculationConfig.set_id == calculation_set_id)

        with self.session_manager.session() as session:
            configs = (session.execute(statement)).scalars().all()

            return configs

    def get(self, calculation_set_id: str, config: CalculationConfig) -> CalculationConfig | None:
        """Get a single calculation config matching the provided filters.

        Args:
            calculation_set_id (str): Id of the calculation set.
            config (CalculationConfig): Calculation config.

        Returns:
            CalculationConfig | None: Calculation config or None if not found.
        """

        statement = select(CalculationConfig).where(
            and_(
                CalculationConfig.set_id == calculation_set_id,
                CalculationConfig.method == config.method,
                CalculationConfig.parameters == config.parameters,
                CalculationConfig.read_hetatm == config.read_hetatm,
                CalculationConfig.ignore_water == config.ignore_water,
                CalculationConfig.permissive_types == config.permissive_types,
            )
        )

        with self.session_manager.session() as session:
            config = (session.execute(statement)).scalars().first()

            return config

    def delete(self, config_id: str) -> None:
        """Delete all calculation configs for given calculation set.

        Args:
            calculation_set_id (str): Id of the calculation set.
            config (CalculationConfig): Calculation config.
        """

        statement = select(CalculationConfig).where(CalculationConfig.id == config_id)

        with self.session_manager.session() as session:
            config = (session.execute(statement)).scalars().first()

            if config is None:
                return

            session.delete(config)
            session.commit()

    def store(self, config: CalculationConfig) -> CalculationConfig:
        """Store a single calculation config in the database.
           If a given config already exists, it is returned.

        Args:
            config (CalculationConfig): Calculation config.

        Raises:
            ValueError: If the calculation set to which the calculation config belongs is not found.

        Returns:
            CalculationConfig: Stored calculation config.
        """

        calculation_set = self.set_repository.get(config.set_id)

        if calculation_set is None:
            raise ValueError("Calculation set not found.")

        exists = self.get(config.set_id, config)

        if exists is not None:
            return exists

        with self.session_manager.session() as session:
            session.add(config)
            session.commit()
            session.refresh(config)
            return config
