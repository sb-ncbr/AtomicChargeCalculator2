import traceback
from dataclasses import asdict

from core.logging.base import LoggerBase
from core.models.calculation import (
    CalculationConfigDto,
    CalculationDto,
    CalculationResultDto,
    CalculationSetDto,
    CalculationSetPreviewDto,
    CalculationsFilters,
)
from core.models.paging import PagedList
from db.models.calculation.calculation import Calculation
from db.models.calculation.calculation_config import CalculationConfig
from db.models.calculation.calculation_set import CalculationSet
from db.repositories.calculation_config_repository import CalculationConfigRepository
from db.repositories.calculation_repository import CalculationRepository
from db.repositories.calculation_set_repository import (
    CalculationSetFilters,
    CalculationSetRepository,
)


class CalculationStorageService:
    """Service for manipulating calculations in the database."""

    def __init__(
        self,
        logger: LoggerBase,
        set_repository: CalculationSetRepository,
        calculation_repository: CalculationRepository,
        config_repository: CalculationConfigRepository,
    ):
        self.set_repository = set_repository
        self.set_repository = set_repository
        self.calculation_repository = calculation_repository
        self.config_repository = config_repository
        self.logger = logger

    def store_calculation_set(
        self, computation_id: str, user_id: str | None, data: list[CalculationResultDto]
    ) -> CalculationSetDto:
        """Store calculation set to database."""

        self.logger.info(f"Storing calculation set {computation_id}.")

        try:
            calculations: list[Calculation] = [
                Calculation(
                    file=calculation.file,
                    file_hash=calculation.file_hash,
                    charges=calculation.charges,
                )
                for result in data
                for calculation in result.calculations
            ]

            configs: list[CalculationConfig] = [
                CalculationConfig(**asdict(result.config)) for result in data
            ]

            calculation_set_to_store = CalculationSet(
                id=computation_id, calculations=calculations, configs=configs, user_id=user_id
            )

            calculation_set = self.set_repository.store(calculation_set_to_store)
            return CalculationSetDto(
                id=calculation_set.id,
                calculations=[CalculationDto.model_validate(calc) for calc in calculations],
                configs=[CalculationConfigDto.model_validate(config) for config in configs],
            )
        except Exception as e:
            self.logger.error(
                f"Error storing calculation set {computation_id}: {traceback.format_exc()}"
            )
            raise e

    def delete_calculation_set(self, computation_id: str) -> None:
        """Delete calculation set from database."""

        try:
            self.logger.info(f"Deleting calculation set {computation_id}.")
            self.set_repository.delete(computation_id)
        except Exception as e:
            self.logger.error(
                f"Error deleting calculation set {computation_id}: {traceback.format_exc()}"
            )
            raise e

    def get_calculation(
        self, computation_id: str, filters: CalculationsFilters
    ) -> CalculationDto | None:
        """Get calculation from database based on filters."""

        try:
            self.logger.info("Getting calculation from database.")
            calculation = self.calculation_repository.get(computation_id, filters)

            return CalculationDto.model_validate(calculation) if calculation is not None else None
        except Exception as e:
            self.logger.error(f"Error getting calculation from database: {traceback.format_exc()}")
            raise e

    def get_calculations(
        self, filters: CalculationSetFilters
    ) -> PagedList[CalculationSetPreviewDto]:
        """Get calculations from database based on filters."""

        try:
            self.logger.info("Getting calculations from database.")
            calculations_list = self.set_repository.get_all(filters)
            calculations_list.items = [
                CalculationSetPreviewDto.model_validate(
                    {
                        "id": calculation_set.id,
                        "files": {
                            calculation.file: calculation.info
                            for calculation in set(calculation_set.calculations)
                        },
                        "configs": calculation_set.configs,
                        "created_at": calculation_set.created_at,
                    }
                )
                for calculation_set in calculations_list.items
            ]

            return PagedList[CalculationSetPreviewDto].model_validate(calculations_list)
        except Exception as e:
            self.logger.error(f"Error getting calculations from database: {traceback.format_exc()}")
            raise e

    def get_calculation_set(self, computation_id: str) -> CalculationSetDto:
        """Get calculation set from database."""

        try:
            self.logger.info(f"Getting calculation set {computation_id}.")
            return self.set_repository.get(computation_id)
        except Exception as e:
            self.logger.error(
                f"Error getting calculation set {computation_id}: {traceback.format_exc()}"
            )
            raise e

    def store_calculation(self, calculation: Calculation) -> Calculation:
        """Store calculation to database."""

        try:
            self.logger.info(f"Storing calculation to set {calculation.set_id}.")
            return self.calculation_repository.store(calculation)
        except Exception as e:
            self.logger.error(
                f"Error storing calculation to set {calculation.set_id}: {traceback.format_exc()}"
            )
            raise e

    def store_config(self, config: CalculationConfig) -> CalculationConfig:
        try:
            self.logger.info(f"Storing config to set {config.set_id}.")
            return self.config_repository.store(config)
        except Exception as e:
            self.logger.error(
                f"Error storing config to set {config.set_id}: {traceback.format_exc()}"
            )
            raise e
