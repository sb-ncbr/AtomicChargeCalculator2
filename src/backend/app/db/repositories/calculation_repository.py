"""This module provides a repository for calculations."""

from sqlalchemy import and_, Select, func, select
from sqlalchemy.orm import joinedload, Session


from models.paging import PagedList
from models.calculation import CalculationsFilters

from db.schemas.calculation import AdvancedSettings, Calculation, CalculationConfig
from db.repositories.calculation_set_repository import CalculationSetRepository


class CalculationRepository:
    """Repository for managing calculation sets."""

    def __init__(
        self,
        set_repository: CalculationSetRepository,
    ):
        self.set_repository = set_repository

    def get(self, session: Session, filters: CalculationsFilters) -> Calculation | None:
        """Get a single previous calculation by id.

        Args:
            calculation_id (str): Calculation id to get.

        Returns:
            Calculation: Calculation set.
        """

        statement = (
            select(Calculation)
            .join(CalculationConfig)
            .join(AdvancedSettings)
            .options(joinedload(Calculation.config), joinedload(Calculation.advanced_settings))
            .where(
                and_(
                    Calculation.file_hash == filters.hash,
                    CalculationConfig.method == filters.method,
                    CalculationConfig.parameters == filters.parameters,
                    AdvancedSettings.read_hetatm == filters.read_hetatm,
                    AdvancedSettings.ignore_water == filters.ignore_water,
                    AdvancedSettings.permissive_types == filters.permissive_types,
                )
            )
        )

        calculation = (session.execute(statement)).unique().scalars().first()
        return calculation

    def store(self, session: Session, calculation: Calculation) -> Calculation:
        """Store a single calculation set in the database.

        Args:
            calculation_set (Calculation): Calculation to store.

        Returns:
            Calculation: Stored calculation set.
        """

        session.add(calculation)

        return calculation

    def _paginate(
        self, session: Session, statement: Select, page: int, page_size: int
    ) -> PagedList[Calculation]:
        total_statement = select(func.count()).select_from(statement)
        items_statement = statement.limit(page_size).offset((page - 1) * page_size)

        total_count = (session.execute(total_statement)).scalar()
        items = (session.execute(items_statement)).scalars(Calculation).all()

        return PagedList[Calculation](
            page=page, page_size=page_size, total_count=total_count, items=items
        )
