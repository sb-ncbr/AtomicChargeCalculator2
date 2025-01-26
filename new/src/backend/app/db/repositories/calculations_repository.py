"""This module contains the CalculationsRepository class."""

from contextlib import AbstractContextManager
from typing import Callable
from sqlalchemy.sql.expression import and_
from sqlalchemy.orm.session import Session

from core.models.paging import PagedList, PagingFilters
from core.models.calculation import (
    ChargeCalculationConfig,
    CalculationDto,
    CalculationsFilters,
    ChargeCalculationResult,
)

from db.models.calculation import Calculation


class CalculationsRepository:
    """Calculations repository."""

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory

    def get_all(self, filters: PagingFilters) -> PagedList[CalculationDto]:
        """Get all previous calculations matching the provided filters."""

        with self.session_factory() as session:
            calculations_query = session.query(Calculation)
            calculations = PagedList(
                query=calculations_query, page=filters.page, page_size=filters.page_size
            )
            calculations.data = [
                CalculationDto.model_validate(calculation) for calculation in calculations.data
            ]

            return calculations

    def get(self, filters: CalculationsFilters) -> CalculationDto | None:
        """Get a single previous calculation matching the provided filters."""

        with self.session_factory() as session:
            calculation = (
                session.query(Calculation)
                .filter(
                    and_(
                        Calculation.file_hash == filters.hash,
                        Calculation.method == filters.method,
                        Calculation.parameters == filters.parameters,
                        Calculation.read_hetatm == filters.read_hetatm,
                        Calculation.ignore_water == filters.ignore_water,
                    )
                )
                .first()
            )
            return CalculationDto.model_validate(calculation) if calculation else None

    def store(
        self, calculation_result: ChargeCalculationResult, config: ChargeCalculationConfig
    ) -> CalculationDto:
        """Store a single calculation result in the database."""

        with self.session_factory() as session:
            calculation = Calculation(
                file_hash=calculation_result.file_hash,
                method=config.method,
                parameters=config.parameters,
                read_hetatm=config.read_hetatm,
                ignore_water=config.ignore_water,
                charges=calculation_result.charges,
            )

            session.add(calculation)
            session.commit()
            session.refresh(calculation)

            return CalculationDto.model_validate(calculation)

    def store_multiple(
        self, calculation_results: list[ChargeCalculationResult], config: ChargeCalculationConfig
    ) -> None:
        """Store multiple calculation results in the database."""

        with self.session_factory() as session:
            calculations = (
                Calculation(
                    file_hash=result.file_hash,
                    method=config.method,
                    parameters=config.parameters,
                    read_hetatm=config.read_hetatm,
                    ignore_water=config.ignore_water,
                    charges=result.charges,
                )
                for result in calculation_results
                if not result.error
            )
            session.bulk_save_objects(calculations)
            session.commit()

    def delete(self, calculation_id: str) -> None:
        """Delete a single calculation from the database by id."""

        with self.session_factory() as session:
            calculation: Calculation = (
                session.query(Calculation).filter(Calculation.id == calculation_id).first()
            )

            if not calculation:
                return

            session.delete(calculation)
            session.commit()
