"""This module provides a repository for calculation sets."""

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import Select, func, select, and_
from sqlalchemy.orm import joinedload, Session


from models.paging import PagedList, PagingFilters

from db.schemas.calculation import CalculationSet


@dataclass
class CalculationSetFilters(PagingFilters):
    """Filters for calculation sets."""

    order_by: str
    order: Literal["asc", "desc"]
    user_id: str


class CalculationSetRepository:
    """Repository for managing calculation sets."""

    def get_all(
        self, session: Session, filters: CalculationSetFilters
    ) -> PagedList[CalculationSet]:
        """Get all previous calculations matching the provided filters.

        Args:
            filters (PagingFilters): Filters for paging.

        Returns:
            PagedList[CalculationSet]: Paged list of calculation sets.
        """

        statement = (
            select(CalculationSet)
            .options(joinedload(CalculationSet.configs))
            .options(joinedload(CalculationSet.advanced_settings))
            .options(joinedload(CalculationSet.molecule_set_stats))
            .order_by(getattr(getattr(CalculationSet, filters.order_by), filters.order)())
            # Return only sets having some calculations
            .where(and_(CalculationSet.configs.any(), CalculationSet.user_id == filters.user_id))
        )

        calculations = self._paginate(session, statement, filters.page, filters.page_size)

        return calculations

    def get(self, session: Session, calculation_id: str) -> CalculationSet | None:
        """Get a single previous calculation by id.

        Args:
            calculation_id (str): Calculation id to get.

        Returns:
            CalculationSet: Calculation set.
        """

        statement = (
            select(CalculationSet)
            .options(
                joinedload(CalculationSet.configs),
                joinedload(CalculationSet.advanced_settings),
                joinedload(CalculationSet.molecule_set_stats),
            )
            .execution_options(populate_existing=True)
            .where(CalculationSet.id == calculation_id)
        )

        calculation_set = (session.execute(statement)).unique().scalars(CalculationSet).first()
        return calculation_set

    def delete(self, session: Session, calculation_id: str) -> None:
        """Delete a single previous calculation by id.

        Args:
            calculation_id (str): Calculation id to delete.
        """

        statement = select(CalculationSet).where(CalculationSet.id == calculation_id)

        calculation_set = (session.execute(statement)).scalars(CalculationSet).first()

        if not calculation_set:
            return

        session.delete(calculation_set)

    def store(self, session: Session, calculation_set: CalculationSet) -> None:
        """Store a single calculation set in the database.

        Args:
            calculation_set (CalculationSet): Calculation set to store.

        Returns:
            CalculationSet: Stored calculation set.
        """

        if self.get(session, calculation_set.id) is None:
            session.add(calculation_set)

    def _paginate(
        self, session: Session, statement: Select, page: int, page_size: int
    ) -> PagedList[CalculationSet]:
        total_statement = select(func.count()).select_from(statement)
        items_statement = statement.limit(page_size).offset((page - 1) * page_size)

        total_count = (session.execute(total_statement)).unique().scalar()
        items = (session.execute(items_statement)).unique().scalars(CalculationSet).all()

        return PagedList[CalculationSet](
            page=page, page_size=page_size, total_count=total_count, items=items
        )
