"""ChargeFW2 service module."""

import asyncio
import os
from pathlib import Path
import traceback

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple


# Temporary solution to get Molecules class
from chargefw2 import Molecules

from models.calculation import (
    CalculationDto,
    CalculationConfigDto,
    CalculationResultDto,
)
from models.molecule_info import MoleculeSetStats
from models.method import Method
from models.parameters import Parameters
from models.setup import AdvancedSettingsDto
from models.suitable_methods import SuitableMethods

from integrations.chargefw2.base import ChargeFW2Base

from api.v1.constants import CHARGES_OUTPUT_EXTENSION


from services.io import IOService
from services.logging.base import LoggerBase
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

    async def get_suitable_methods(
        self, file_hashes: list[str], user_id: str | None
    ) -> SuitableMethods:
        """Get suitable methods for charge calculation based on file hashes."""

        try:
            self.logger.info(f"Getting suitable methods for file hashes '{file_hashes}'")

            return await self._find_suitable_methods(file_hashes, user_id)
        except Exception as e:
            self.logger.error(
                f"Error getting suitable methods for file hashes '{file_hashes}': {e}"
            )
            raise e

    async def get_computation_suitable_methods(
        self, computation_id: str, user_id: str | None
    ) -> SuitableMethods:
        """Get suitable methods for charge calculation based on files in the provided directory."""

        try:
            self.logger.info(f"Getting suitable methods for computation '{computation_id}'")

            workdir = self.io.get_inputs_path(computation_id, user_id)
            file_hashes = [self.io.parse_filename(file)[0] for file in self.io.listdir(workdir)]

            return await self._find_suitable_methods(file_hashes, user_id)
        except Exception as e:
            self.logger.error(
                f"Error getting suitable methods for computation '{computation_id}': {e}"
            )
            raise e

    async def _find_suitable_methods(
        self, file_hashes: list[str], user_id: str | None
    ) -> SuitableMethods:
        """Helper method to find suitable methods for calculation."""

        suitable_methods = Counter()
        workdir = self.io.get_file_storage_path(user_id)

        dir_contents = self.io.listdir(workdir)
        for file_hash in file_hashes:
            file = next(
                (f for f in dir_contents if self.io.parse_filename(f)[0] == file_hash), None
            )
            if file is None:
                self.logger.warn(f"File with hash {file_hash} not found in {workdir}, skipping.")
                continue

            input_file = os.path.join(workdir, file)
            molecules = await self.read_molecules(input_file)
            methods: list[tuple[Method, list[Parameters]]] = await self._run_in_executor(
                self.chargefw2.get_suitable_methods, molecules
            )
            for method, parameters in methods:
                if not parameters or len(parameters) == 0:
                    suitable_methods[(method,)] += 1
                else:
                    for p in parameters:
                        suitable_methods[(method, p)] += 1

        all_valid = [
            pair for pair in suitable_methods if suitable_methods[pair] == len(file_hashes)
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

        parameters_with_metadata = {
            method.internal_name: params for method, params in parameters.items()
        }
        return SuitableMethods(methods=methods, parameters=parameters_with_metadata)

    async def get_available_parameters(self, method: str) -> list[Parameters]:
        """Get available parameters for charge calculation method."""

        try:
            self.logger.info(f"Getting available parameters for method {method}.")
            parameters = await self._run_in_executor(
                self.chargefw2.get_available_parameters, method
            )

            return parameters
        except Exception as e:
            self.logger.error(f"Error getting available parameters for method {method}: {e}")
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

    async def _calculate_charges(
        self,
        user_id: str,
        computation_id: str | None,
        settings: AdvancedSettingsDto,
        config: CalculationConfigDto,
        file_hashes: list[str],
    ) -> CalculationResultDto:
        """Calculate charges for provided files."""

        workdir = self.io.get_file_storage_path(user_id)

        semaphore = asyncio.Semaphore(4)  # limit to 4 concurrent calculations

        async def process_file(
            file_hash: str, config: CalculationConfigDto
        ) -> CalculationDto | None:
            file_name = next(
                (
                    file
                    for file in self.io.listdir(workdir)
                    if self.io.parse_filename(file)[0] == file_hash
                ),
                None,
            )

            if file_name is None:
                self.logger.warn(f"File with hash {file_hash} not found in {workdir}, skipping.")
                return

            async with semaphore:
                print("Calculating charges for file", file_name, config.method)
                charges_dir = self.io.get_charges_path(computation_id, user_id)
                self.io.create_dir(charges_dir)

                full_path = os.path.join(workdir, file_name)
                file_name = self.io.parse_filename(file_name)[1]

                molecules = await self.read_molecules(
                    full_path,
                    settings.read_hetatm,
                    settings.ignore_water,
                    settings.permissive_types,
                )

                charges = await self._run_in_executor(
                    self.chargefw2.calculate_charges,
                    molecules,
                    config.method,
                    config.parameters,
                    charges_dir,
                )

                result = CalculationDto(
                    file=file_name, file_hash=file_hash, charges=charges, config=config
                )

                return result

        try:
            calculations = [
                calculation
                for calculation in await asyncio.gather(
                    *[process_file(file_hash, config) for file_hash in file_hashes],
                    return_exceptions=False,  # TODO: what should happen if only one computation fails?
                )
                if calculation is not None
            ]
            config_dto = CalculationConfigDto(
                method=config.method,
                parameters=config.parameters,
            )

            return CalculationResultDto(
                config=config_dto,
                calculations=calculations,
            )
        except Exception as e:
            self.logger.error(f"Error calculating charges: {traceback.format_exc()}")
            raise e

    async def calculate_charges(
        self,
        computation_id: str,
        settings: AdvancedSettingsDto,
        data: Tuple[CalculationConfigDto, list[str]],
        user_id: str | None,
    ) -> list[CalculationResultDto]:
        """Calculate charges for provided files.

        Args:
            computation_id (str): Computation id.
            data (Tuple[CalculationConfigDto, list[str]]): Dictionary of configs and file_hashes.
            user_id (str): User id making the calculation.

        Returns:
            ChargeCalculationResult: List of successful calculations.
                Failed calculations are skipped.
        """

        calculations = await asyncio.gather(
            *[
                self._process_config(user_id, computation_id, settings, file_hashes, config)
                for config, file_hashes in data.items()
            ],
            return_exceptions=False,
        )
        configs = [calculation.config for calculation in calculations]

        await self.io.store_configs(computation_id, configs, user_id)

        return calculations

    async def save_charges(
        self,
        settings: AdvancedSettingsDto,
        computation_id: str,
        results: list[CalculationResultDto],
        user_id: str | None,
    ) -> None:
        workdir = self.io.get_file_storage_path(user_id)
        charges_dir = self.io.get_charges_path(computation_id, user_id)
        self.io.create_dir(charges_dir)

        

        for result in results:
            for calculation in result.calculations:
                file_path = str(Path(workdir) / f"{calculation.file_hash}_{calculation.file}")
                molecules = await self.read_molecules(
                    file_path,
                    settings.read_hetatm,
                    settings.ignore_water,
                    settings.permissive_types,
                )
                config = calculation.config
                await self._run_in_executor(
                    self.chargefw2.save_charges,
                    calculation.charges,
                    molecules,
                    config.method,
                    config.parameters,
                    charges_dir,
                )

    async def _process_config(
        self,
        user_id: str | None,
        computation_id: str,
        settings: AdvancedSettingsDto,
        file_hashes: list[str],
        config: CalculationConfigDto,
    ) -> CalculationResultDto:
        if not config.method:
            # No method provided -> use most suitable method and parameters
            suitable = await self.get_computation_suitable_methods(computation_id, user_id)

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

        return await self._calculate_charges(user_id, computation_id, settings, config, file_hashes)

    async def info(self, path: str) -> MoleculeSetStats:
        """Get information about the provided file."""

        try:
            self.logger.info(f"Getting info for file {path}.")

            molecules = await self.read_molecules(path)
            info = molecules.info()

            return MoleculeSetStats(info.to_dict())
        except Exception as e:
            self.logger.error(f"Error getting info for file {path}: {traceback.format_exc()}")
            raise e

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

    def delete_calculation(self, computation_id: str, user_id: str) -> None:
        """Delete the provided computation (from database and filesystem).

        Args:
            computation_id (str): Computation id.
            user_id (str): User id.

        Raises:
            e: Error deleting computation.
        """
        try:
            self.calculation_storage.delete_calculation_set(computation_id)
            self.io.delete_computation(computation_id, user_id)
        except Exception as e:
            self.logger(f"Error deleting computation {computation_id}: {traceback.format_exc()}")
            raise e
