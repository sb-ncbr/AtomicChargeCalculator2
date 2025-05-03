"""This module provides a repository for calculation configs."""

from sqlalchemy import and_, select
from sqlalchemy.orm import Session


from db.schemas.calculation import CalculationConfig
from db.repositories.calculation_set_repository import CalculationSetRepository


class CalculationConfigRepository:
    """Repository for managing calculation configs."""

    def __init__(
        self,
        set_repository: CalculationSetRepository,
    ):
        self.set_repository = set_repository

    def get(
        self, session: Session, method: str, parameters: str | None
    ) -> CalculationConfig | None:
        """Get a single calculation config matching the provided filters.

        Args:
            method (str): Empirical method.
            parameters (str | None): Method parameters (if any).

        Returns:
            CalculationConfig | None: Calculation config or None if not found.
        """

        statement = select(CalculationConfig).where(
            and_(
                CalculationConfig.method == method,
                CalculationConfig.parameters == parameters,
            )
        )

        config = (session.execute(statement)).scalars().first()
        return config
