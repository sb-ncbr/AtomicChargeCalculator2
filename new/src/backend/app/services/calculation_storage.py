import traceback

from models.calculation import (
    CalculationConfigDto,
    CalculationDto,
    CalculationResultDto,
    CalculationSetDto,
    CalculationSetPreviewDto,
    CalculationsFilters,
    ChargeCalculationConfigDto,
)
from models.paging import PagedList
from models.molecule_info import MoleculeSetStats
from db.models.calculation.calculation import Calculation
from db.models.calculation.calculation_config import CalculationConfig
from db.models.calculation.calculation_set import CalculationSet
from db.models.moleculeset_stats import AtomTypeCount, MoleculeSetStats as MoleculeSetStatsModel
from db.repositories.calculation_config_repository import CalculationConfigRepository
from db.repositories.calculation_repository import CalculationRepository
from db.repositories.calculation_set_repository import (
    CalculationSetFilters,
    CalculationSetRepository,
)
from db.repositories.moleculeset_stats_repository import MoleculeSetStatsRepository

from services.logging.base import LoggerBase


class CalculationStorageService:
    """Service for manipulating calculations in the database."""

    def __init__(
        self,
        logger: LoggerBase,
        set_repository: CalculationSetRepository,
        calculation_repository: CalculationRepository,
        config_repository: CalculationConfigRepository,
        stats_repository: MoleculeSetStatsRepository,
    ):
        self.set_repository = set_repository
        self.set_repository = set_repository
        self.calculation_repository = calculation_repository
        self.config_repository = config_repository
        self.stats_repository = stats_repository
        self.logger = logger

    def get_info(self, file_hash: str) -> MoleculeSetStats | None:
        # Getting info manually due to lazy loading issue

        info = self.stats_repository.get(file_hash)

        if info is None:
            return None

        info_dict = {
            "total_molecules": info.total_molecules,
            "total_atoms": info.total_atoms,
            "atom_type_counts": [vars(count) for count in info.atom_type_counts],
        }

        return MoleculeSetStats(info_dict)

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
                            calculation.file: self.get_info(calculation.file_hash)
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

    def get_calculation_set(self, computation_id: str) -> CalculationSetDto | None:
        """Get calculation set from database."""

        try:
            self.logger.info(f"Getting calculation set {computation_id}.")
            return self.set_repository.get(computation_id)
        except Exception as e:
            self.logger.error(
                f"Error getting calculation set {computation_id}: {traceback.format_exc()}"
            )
            raise e

    def store_file_info(self, file_hash: str, info: MoleculeSetStats) -> MoleculeSetStats:
        """Store file info to database."""

        try:
            self.logger.info(f"Storing stats of file with hash '{file_hash}'.")
            info_model = MoleculeSetStatsModel(
                file_hash=file_hash,
                total_molecules=info.total_molecules,
                total_atoms=info.total_atoms,
                atom_type_counts=[
                    AtomTypeCount(symbol=count.symbol, count=count.count)
                    for count in info.atom_type_counts
                ],
            )
            return self.stats_repository.store(info_model)
        except Exception as e:
            self.logger.error(
                f"Error storing stats of file with hash '{file_hash}': "
                + f"{traceback.format_exc()}"
            )
            raise e

    def store_calculation_results(
        self, computation_id: str, results: list[CalculationResultDto], user_id: str | None
    ) -> None:
        """Store calculation results to database."""

        unique_configs = {}

        existing_calculation_set = self.set_repository.get(computation_id)

        if existing_calculation_set:
            calculation_set = existing_calculation_set
        else:
            calculation_set = CalculationSet(id=computation_id, user_id=user_id)

        for result in results:
            config_key = (
                result.config.method,
                result.config.parameters,
                result.config.read_hetatm,
                result.config.ignore_water,
                result.config.permissive_types,
            )

            config = CalculationConfig(
                method=result.config.method,
                parameters=result.config.parameters,
                read_hetatm=result.config.read_hetatm,
                ignore_water=result.config.ignore_water,
                permissive_types=result.config.permissive_types,
                set_id=computation_id,
            )

            config_exists = self.config_repository.get(computation_id, config)

            if config_exists is None:
                unique_configs[config_key] = config
                result.config = config
            else:
                result.config = config_exists

            for calculation in result.calculations:
                calculation_set.calculations.append(
                    Calculation(
                        file=calculation.file,
                        file_hash=calculation.file_hash,
                        charges=calculation.charges,
                        config=result.config,
                        set_id=computation_id,
                    )
                )

        try:
            self.logger.info(f"Storing calculation results for computation {computation_id}.")
            self.set_repository.store(calculation_set)
        except Exception as e:
            self.logger.error(
                f"Error storing calculation results for computation {computation_id}: {traceback.format_exc()}"
            )
            raise e

    def filter_existing_calculations(
        self, computation_id: str, file_hashes: list[str], configs: list[ChargeCalculationConfigDto]
    ) -> dict[str, list[ChargeCalculationConfigDto]]:
        """Returns a list of hashes and configs that are not in the database."""

        result = {}

        try:
            self.logger.info("Filtering existing calculations.")

            for config in configs:
                for file_hash in file_hashes:
                    filters = CalculationsFilters(
                        hash=file_hash,
                        method=config.method,
                        parameters=config.parameters,
                        read_hetatm=config.read_hetatm,
                        ignore_water=config.ignore_water,
                        permissive_types=config.permissive_types,
                    )

                    existing_calculation = self.calculation_repository.get(computation_id, filters)
                    if existing_calculation is None:
                        if config not in result:
                            result[config] = []

                        result[config].append(file_hash)
                    else:
                        self.logger.info("Existing calculation found for file, skipping.")

            return result
        except Exception as e:
            self.logger.error(f"Error filtering existing calculations: {traceback.format_exc()}")
            raise e

    def get_calculation_results(self, computation_id: str) -> list[CalculationResultDto]:
        """Get calculation results from database."""

        try:
            self.logger.info(f"Getting calculation results for computation {computation_id}.")
            calculation_set = self.set_repository.get(computation_id)

            if not calculation_set:
                return []

            result = [
                CalculationResultDto(
                    config=CalculationConfigDto.model_validate(config),
                    calculations=[
                        CalculationDto.model_validate(calculation)
                        for calculation in calculation_set.calculations
                        if calculation.config == config
                    ],
                )
                for config in calculation_set.configs
            ]

            return result

        except Exception as e:
            self.logger.error(
                f"Error getting calculation results for computation {computation_id}: {traceback.format_exc()}"
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
