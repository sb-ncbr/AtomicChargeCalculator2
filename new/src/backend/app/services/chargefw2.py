"""ChargeFW2 service module."""

import asyncio
import os
import traceback

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict


from fastapi import UploadFile

# Temporary solution to get Molecules class
from chargefw2 import Molecules

from core.integrations.chargefw2.base import ChargeFW2Base
from core.logging.base import LoggerBase
from core.models.calculation import (
    CalculationDto,
    CalculationsFilters,
    ChargeCalculationConfigDto,
    CalculationResultDto,
)
from core.models.molecule_info import MoleculeSetStats
from core.models.method import Method
from core.models.parameters import Parameters
from core.models.suitable_methods import SuitableMethods


from api.v1.constants import CHARGES_OUTPUT_EXTENSION

from db.models.calculation.calculation import Calculation
from db.models.calculation.calculation_config import CalculationConfig


from services.io import IOService
from services.mmcif import MmCIFService
from services.calculation_storage import CalculationStorageService


class ChargeFW2Service:
    """ChargeFW2 service."""

    def __init__(
        self,
        chargefw2: ChargeFW2Base,
        logger: LoggerBase,
        io: IOService,
        mmcif_service: MmCIFService,
        calculation_storage: CalculationStorageService,
        max_workers: int = 4,
    ):
        self.chargefw2 = chargefw2
        self.logger = logger
        self.io = io
        self.mmcif_service = mmcif_service
        self.calculation_storage = calculation_storage
        self.executor = ThreadPoolExecutor(max_workers)

    async def _run_in_executor(self, func, *args, executor=None):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor if executor is None else executor, func, *args
        )

    # Method related operations
    def get_available_methods(self) -> list[Method]:
        """Get available methods for charge calculation."""

        try:
            self.logger.info("Getting available methods.")
            methods = self.chargefw2.get_available_methods()

            return methods
        except Exception as e:
            self.logger.error(f"Error getting available methods: {e}")
            raise e

    async def get_suitable_methods(self, computation_id: str) -> SuitableMethods:
        """Get suitable methods for charge calculation based on files in the provided directory."""

        try:
            self.logger.info(f"Getting suitable methods for computation id  '{computation_id}'")
            return await self._find_suitable_methods(computation_id)
        except Exception as e:
            self.logger.error(
                f"Error getting suitable methods for computation id '{computation_id}': {e}"
            )
            raise e

    async def _find_suitable_methods(self, computation_id: str) -> SuitableMethods:
        """Helper method to find suitable methods for calculation."""
        suitable_methods = Counter()
        workdir = self.io.get_input_path(computation_id)

        dir_contents = self.io.listdir(workdir)
        for file in dir_contents:
            input_file = os.path.join(workdir, file)
            molecules = await self.read_molecules(input_file)
            methods: list[tuple[str, list[str]]] = await self._run_in_executor(
                self.chargefw2.get_suitable_methods, molecules
            )
            for method, parameters in methods:
                if not parameters or len(parameters) == 0:
                    suitable_methods[(method,)] += 1
                else:
                    for p in parameters:
                        suitable_methods[(method, p)] += 1

        all_valid = [
            pair for pair in suitable_methods if suitable_methods[pair] == len(dir_contents)
        ]

        # Remove duplicates from methods
        tmp = {}
        for data in all_valid:
            tmp[data[0]] = None

        methods = list(tmp.keys())

        parameters = defaultdict(list)
        for pair in all_valid:
            if len(pair) == 2:
                parameters[pair[0]].append(pair[1])

        # Add metadata to methods and paremeters
        all_methods_with_metadata = self.get_available_methods()
        methods_with_metadata = [m for m in all_methods_with_metadata if m.internal_name in methods]
        parameters_with_metadata = {
            method: [Parameters(**(await self.get_parameters_metadata(p))) for p in params]
            for method, params in parameters.items()
        }
        return SuitableMethods(methods=methods_with_metadata, parameters=parameters_with_metadata)

    async def get_available_parameters(self, method: str) -> list[Parameters]:
        """Get available parameters for charge calculation method."""

        try:
            self.logger.info(f"Getting available parameters for method {method}.")
            parameters = await self._run_in_executor(
                self.chargefw2.get_available_parameters, method
            )

            return [Parameters(**(await self.get_parameters_metadata(p))) for p in parameters]
        except Exception as e:
            self.logger.error(f"Error getting available parameters for method {method}: {e}")
            raise e

    async def get_parameters_metadata(self, parameters: str) -> list[Parameters]:
        """Get parameters metadata for charge calculation."""

        try:
            self.logger.info(f"Getting parameters metadata: {parameters}")
            parameters_metadata = await self._run_in_executor(
                self.chargefw2.get_parameters_metadata, parameters
            )

            return parameters_metadata
        except Exception as e:
            self.logger.error(f"Error getting parameters metadata: {e}")
            raise e

    async def read_molecules(
        self,
        file_path: str,
        read_hetatm: bool = True,
        ignore_water: bool = False,
        permissive_types: bool = False,
    ) -> Molecules:
        """Load molecules from a file"""
        try:
            self.logger.info(f"Loading molecules from file {file_path}.")
            molecules = await self._run_in_executor(
                self.chargefw2.molecules, file_path, read_hetatm, ignore_water, permissive_types
            )

            return molecules
        except Exception as e:
            self.logger.error(f"Error loading molecules from file {file_path}: {e}")
            raise e

    async def calculate_charges(
        self, computation_id: str, config: CalculationConfig
    ) -> CalculationResultDto:
        """Calculate charges for provided files."""

        workdir = self.io.get_input_path(computation_id)
        charges_dir = self.io.get_charges_path(computation_id)
        self.io.create_dir(charges_dir)

        semaphore = asyncio.Semaphore(4)  # limit to 4 concurrent calculations

        async def process_file(file: str, config: CalculationConfig) -> CalculationDto:
            full_path = os.path.join(workdir, file)
            file_hash = file.split("_", 1)[0]
            file_name = file.split("_", 1)[-1]

            async with semaphore:
                exists = self.calculation_storage.get_calculation(
                    computation_id,
                    CalculationsFilters(
                        hash=file_hash,
                        ignore_water=config.ignore_water,
                        method=config.method,
                        permissive_types=config.permissive_types,
                        parameters=config.parameters,
                        read_hetatm=config.read_hetatm,
                    ),
                )

                if exists is not None:
                    self.logger.info(f"Charges for {file_name} already exist, skipping.")
                    return exists

                molecules = await self.read_molecules(
                    full_path, config.read_hetatm, config.ignore_water, config.permissive_types
                )
                charges = await self._run_in_executor(
                    self.chargefw2.calculate_charges,
                    molecules,
                    config.method,
                    config.parameters,
                    charges_dir,
                )

                info = MoleculeSetStats(molecules.info().to_dict())
                result = CalculationDto(
                    file=file_name, file_hash=file_hash, info=info, charges=charges
                )

                self.calculation_storage.store_calculation(
                    Calculation(
                        file=file_name,
                        file_hash=file_hash,
                        info=asdict(info),
                        charges=charges,
                        set_id=computation_id,
                        config_id=config.id,
                    )
                )

                return result

        try:
            # Process all files concurrently
            inputs = self.io.listdir(workdir)
            calculations = await asyncio.gather(
                *[process_file(file, config) for file in inputs],
                return_exceptions=False,  # TODO: what should happen if only one computation fails?
            )
            config_dto = ChargeCalculationConfigDto(
                method=config.method,
                parameters=config.parameters,
                read_hetatm=config.read_hetatm,
                ignore_water=config.ignore_water,
                permissive_types=config.permissive_types,
            )

            return CalculationResultDto(
                config=config_dto,
                calculations=calculations,
            )
        except Exception as e:
            self.logger.error(f"Error calculating charges: {traceback.format_exc()}")
            raise e

    async def calculate_charges_multi(
        self, computation_id: str, configs: list[ChargeCalculationConfigDto]
    ) -> list[CalculationResultDto]:
        """Calculate charges for provided files.

        Args:
            computation_id (str): Computation id
            configs (list[ChargeCalculationConfig]): List of configurations.

        Returns:
            ChargeCalculationResult: List of successful calculations. Failed calculations are skipped.
        """

        calculations = await asyncio.gather(
            *[self._process_config(computation_id, config) for config in configs],
            return_exceptions=False,
        )
        _ = self.mmcif_service.write_to_mmcif(computation_id, calculations)

        return calculations

    async def _process_config(
        self, computation_id: str, config: CalculationConfig
    ) -> CalculationResultDto:
        if not config.method:
            # No method provided -> use most suitable method and parameters
            suitable = await self.get_suitable_methods(computation_id)

            if len(suitable.methods) == 0:
                self.logger.error(
                    f"No suitable methods found for charge calculation {computation_id}."
                )
                raise Exception("No suitable methods found.")

            config.method = suitable.methods[0].internal_name
            parameters = suitable.parameters.get(config.method, [])
            config.parameters = parameters[0].internal_name if len(parameters) > 0 else None
            self.logger.info(
                f"""No method provided.
                        Using method '{config.method}' with parameters '{config.parameters}'."""
            )

        # store config in db
        # TODO: do not store invalid config
        db_config = self.calculation_storage.store_config(
            CalculationConfig(set_id=computation_id, **asdict(config))
        )
        return await self.calculate_charges(computation_id, db_config)

    async def info(self, file: UploadFile) -> MoleculeSetStats:
        """Get information about the provided file."""

        try:
            workdir = self.io.create_workdir("info")
            new_file_path, _ = await self.io.store_upload_file(file, workdir)

            self.logger.info(f"Getting info for file {file.filename}.")
            molecules = await self.read_molecules(new_file_path)

            info = molecules.info()

            return MoleculeSetStats(info.to_dict())
        except Exception as e:
            self.logger.error(
                f"Error getting info for file {file.filename}: {traceback.format_exc()}"
            )
            raise e
        finally:
            self.io.remove_workdir("info")

    def get_calculation_molecules(self, path: str) -> list[str]:
        """Returns molecules stored in the provided path.

        Args:
            path (str): Path to computation results.

        Raises:
            FileNotFoundError: If the provided path does not exist.

        Returns:
            list[str]: List of molecule names.
        """
        if not self.io.path_exists(path):
            raise FileNotFoundError()

        molecule_files = [
            file for file in self.io.listdir(path) if file.endswith(CHARGES_OUTPUT_EXTENSION)
        ]
        molecules = [file.replace(CHARGES_OUTPUT_EXTENSION, "") for file in molecule_files]

        return molecules
