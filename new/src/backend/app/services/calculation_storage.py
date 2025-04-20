import traceback
from typing import Tuple

from sqlalchemy.orm import Session

from models.calculation import (
    CalculationConfigDto,
    CalculationDto,
    CalculationResultDto,
    CalculationSetPreviewDto,
    CalculationsFilters,
)
from models.paging import PagedList
from models.molecule_info import MoleculeSetStats
from db.schemas.calculation import (
    AdvancedSettings,
    Calculation,
    CalculationConfig,
    CalculationSet,
    CalculationSetStats,
)
from db.schemas.stats import AtomTypeCount, MoleculeSetStats as MoleculeSetStatsModel

from db.repositories.calculation_config_repository import CalculationConfigRepository
from db.repositories.calculation_repository import CalculationRepository
from db.repositories.calculation_set_repository import (
    CalculationSetFilters,
    CalculationSetRepository,
)
from db.repositories.moleculeset_stats_repository import MoleculeSetStatsRepository

from models.setup import AdvancedSettingsDto
from db.repositories.advanced_settings_repository import AdvancedSettingsRepository
from db.database import SessionManager
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
        advanced_settings_repository: AdvancedSettingsRepository,
        session_manager: SessionManager,
    ):
        self.set_repository = set_repository
        self.calculation_repository = calculation_repository
        self.config_repository = config_repository
        self.stats_repository = stats_repository
        self.advanced_settings_repository = advanced_settings_repository
        self.session_manager = session_manager
        self.logger = logger

    def get_info(self, session: Session, file_hash: str) -> MoleculeSetStats | None:
        # Getting info manually due to lazy loading issue

        info = self.stats_repository.get(session, file_hash)

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
            with self.session_manager.session() as session:
                self.logger.info("Getting calculations from database.")
                calculations_list = self.set_repository.get_all(session, filters)
                calculations_list.items = [
                    CalculationSetPreviewDto.model_validate(
                        {
                            "id": calculation_set.id,
                            "files": {
                                stats_assoc.file_name: self.get_info(
                                    session, stats_assoc.molecule_set_id
                                )
                                for stats_assoc in calculation_set.molecule_set_stats_associations
                            },
                            "configs": calculation_set.configs,
                            "settings": AdvancedSettingsDto.model_validate(
                                vars(calculation_set.advanced_settings)
                            ),
                            "created_at": calculation_set.created_at,
                        }
                    )
                    for calculation_set in calculations_list.items
                ]

            return PagedList[CalculationSetPreviewDto].model_validate(calculations_list)
        except Exception as e:
            self.logger.error(f"Error getting calculations from database: {traceback.format_exc()}")
            raise e

    def get_calculation_set(self, computation_id: str) -> CalculationSet | None:
        """Get calculation set from database."""

        try:
            self.logger.info(f"Getting calculation set {computation_id}.")
            with self.session_manager.session() as session:
                return self.set_repository.get(session, computation_id)
        except Exception as e:
            self.logger.error(
                f"Error getting calculation set {computation_id}: {traceback.format_exc()}"
            )
            raise e

    def store_file_info(self, file_hash: str, info: MoleculeSetStats) -> MoleculeSetStats:
        """Store file info to database."""

        try:
            with self.session_manager.session() as session:
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

                return self.stats_repository.store(session, info_model)
        except Exception as e:
            self.logger.error(
                f"Error storing stats of file with hash '{file_hash}': "
                + f"{traceback.format_exc()}"
            )
            raise e

    def store_calculation_results(
        self,
        computation_id: str,
        settings: AdvancedSettingsDto,
        results: list[CalculationResultDto],
        user_id: str | None,
    ) -> None:
        try:
            self.logger.info(f"Storing calculation results for computation {computation_id}.")

            with self.session_manager.session() as session:
                settings_entity = self._get_or_create_advanced_settings(session, settings)
                calculation_set = self._get_or_create_calculation_set(
                    session, computation_id, user_id, settings_entity
                )

                calculations = []
                added_stats = set()

                for result in results:
                    config_entity = self._get_or_create_config(
                        session, result.config, calculation_set
                    )

                    new_calculations, files = self._process_calculations(
                        session, result, config_entity, settings_entity
                    )
                    calculations.extend(new_calculations)

                    self._add_molecule_stats(session, calculation_set, files, added_stats)

                for calculation in calculations:
                    self.calculation_repository.store(session, calculation)

                self.set_repository.store(session, calculation_set)

        except Exception as e:
            self.logger.error(
                f"Error storing calculation results for computation {computation_id}."
            )
            raise e

    def setup_calculation(
        self,
        computation_id: str,
        settings: AdvancedSettingsDto,
        file_hashes: list[str],
        user_id: str | None,
    ) -> None:
        """Setup calculation in database."""

        try:
            self.logger.info("Setting up calculation.")

            with self.session_manager.session() as session:
                settings_entity = self._get_or_create_advanced_settings(session, settings)

                calculation_set = CalculationSet(
                    id=computation_id,
                    user_id=user_id,
                    advanced_settings=settings_entity,
                )

                for file_hash in file_hashes:
                    calculation_set.molecule_set_stats.append(
                        self.stats_repository.get(session, file_hash)
                    )

                self.set_repository.store(session, calculation_set)
        except Exception as e:
            self.logger.error(f"Error setting up calculation: {traceback.format_exc()}")
            raise e

    def filter_existing_calculations(
        self,
        settings: AdvancedSettingsDto,
        file_hashes: list[str],
        configs: list[CalculationConfigDto],
    ) -> Tuple[
        dict[str, list[CalculationConfigDto]], dict[CalculationConfigDto, list[CalculationDto]]
    ]:
        """Returns a list of hashes and configs that are not in the database."""

        to_calculate = {}
        cached = {}

        try:
            self.logger.info("Filtering existing calculations.")

            with self.session_manager.session() as session:
                for config in configs:
                    for file_hash in file_hashes:
                        filters = CalculationsFilters(
                            hash=file_hash,
                            method=config.method,
                            parameters=config.parameters,
                            read_hetatm=settings.read_hetatm,
                            ignore_water=settings.ignore_water,
                            permissive_types=settings.permissive_types,
                        )

                        existing_calculation = self.calculation_repository.get(session, filters)
                        if existing_calculation is None:
                            if config not in to_calculate:
                                to_calculate[config] = []

                            to_calculate[config].append(file_hash)
                        else:
                            if config not in cached:
                                cached[config] = []

                            cached[config].append(
                                CalculationDto(
                                    file=existing_calculation.file_name,
                                    file_hash=existing_calculation.file_hash,
                                    charges=existing_calculation.charges,
                                    config=config,
                                ),
                            )
                            self.logger.info(
                                f"Existing calculation found for file '{file_hash}', skipping."
                            )

            return to_calculate, cached
        except Exception as e:
            self.logger.error(f"Error filtering existing calculations: {traceback.format_exc()}")
            raise e

    def get_calculation_results(self, computation_id: str) -> list[CalculationResultDto]:
        """Get calculation results from database."""

        try:
            self.logger.info(f"Getting calculation results for computation {computation_id}.")
            with self.session_manager.session() as session:
                calculation_set = self.set_repository.get(session, computation_id)

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
            with self.session_manager.session() as session:
                self.set_repository.delete(session, computation_id)
        except Exception as e:
            self.logger.error(
                f"Error deleting calculation set {computation_id}: {traceback.format_exc()}"
            )
            raise e

    def _get_or_create_advanced_settings(
        self, session: Session, settings: AdvancedSettingsDto
    ) -> AdvancedSettings:
        """Get existing settings or create new."""

        settings_entity = self.advanced_settings_repository.get(session, settings)
        if settings_entity is None:
            settings_entity = AdvancedSettings(
                ignore_water=settings.ignore_water,
                read_hetatm=settings.read_hetatm,
                permissive_types=settings.permissive_types,
            )
            self.advanced_settings_repository.store(session, settings_entity)
        return settings_entity

    def _get_or_create_calculation_set(
        self,
        session: Session,
        computation_id: str,
        user_id: str | None,
        settings_entity: AdvancedSettings,
    ) -> CalculationSet:
        """Get existing calculation set or create new."""

        calculation_set = self.set_repository.get(session, computation_id)
        if calculation_set is None:
            calculation_set = CalculationSet(
                id=computation_id,
                user_id=user_id,
                advanced_settings=settings_entity,
            )
            self.set_repository.store(session, calculation_set)

        return calculation_set

    def _get_or_create_config(
        self, session: Session, config: CalculationConfigDto, calculation_set: CalculationSet
    ) -> CalculationConfig:
        """Get existing config or create new."""

        existing_config = self.config_repository.get(session, config.method, config.parameters)

        if existing_config is None:
            config_entity = CalculationConfig(method=config.method, parameters=config.parameters)
        else:
            config_entity = existing_config

        if config_entity not in calculation_set.configs:
            calculation_set.configs.append(config_entity)

        return config_entity

    def _process_calculations(
        self,
        session: Session,
        result: CalculationResultDto,
        config_entity: CalculationConfig,
        settings_entity: AdvancedSettings,
    ) -> tuple[list[Calculation], dict[str, str]]:
        """Process calculation results and return new calculations and files (file_hash -> file)."""

        new_calculations = []
        files = {}

        for calculation in result.calculations:
            files[calculation.file_hash] = calculation.file

            calculation_exists = self.calculation_repository.get(
                session,
                CalculationsFilters(
                    hash=calculation.file_hash,
                    method=calculation.config.method,
                    parameters=calculation.config.parameters,
                    read_hetatm=settings_entity.read_hetatm,
                    ignore_water=settings_entity.ignore_water,
                    permissive_types=settings_entity.permissive_types,
                ),
            )

            if calculation_exists is None:
                new_calculations.append(
                    Calculation(
                        file_name=calculation.file,
                        file_hash=calculation.file_hash,
                        charges=calculation.charges,
                        config=config_entity,
                        advanced_settings=settings_entity,
                    )
                )

        return new_calculations, files

    def _add_molecule_stats(
        self,
        session: Session,
        calculation_set: CalculationSet,
        files: dict[str, str],
        added_stats: set[str],
    ) -> None:
        file_hashes = set(files.keys())
        new_file_hashes = file_hashes - added_stats

        for file_hash in new_file_hashes:
            stats = self.stats_repository.get(session, file_hash)

            if stats is None:
                # This should never happen
                continue

            association = CalculationSetStats(
                molecule_set_id=stats.file_hash,
                file_name=files.get(stats.file_hash),
            )
            calculation_set.molecule_set_stats_associations.append(association)
            added_stats.add(stats.file_hash)
