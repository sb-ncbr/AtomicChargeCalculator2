"""ChargeFW2 service module."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import UploadFile

# Temporary solution to get Molecules class
from chargefw2 import Molecules

from core.integrations.chargefw2.base import ChargeFW2Base
from core.logging.base import LoggerBase
from core.models.calculation import (
    CalculationDto,
    CalculationsFilters,
    ChargeCalculationConfig,
    ChargeCalculationResult,
)
from core.models.paging import PagingFilters, PagedList

from db.repositories.calculations_repository import CalculationsRepository

from services.io import IOService


class ChargeFW2Service:
    """ChargeFW2 service."""

    def __init__(
        self,
        chargefw2: ChargeFW2Base,
        logger: LoggerBase,
        io: IOService,
        calculations_repository: CalculationsRepository,
        max_workers: int = 4,
    ):
        self.chargefw2 = chargefw2
        self.logger = logger
        self.io = io
        self.calculations_repository = calculations_repository
        self.executor = ThreadPoolExecutor(max_workers)

    async def _run_in_executor(self, func, *args, executor=None):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor if executor is None else executor, func, *args
        )

    async def get_available_methods(self) -> list[str]:
        """Get available methods for charge calculation."""

        try:
            self.logger.info("Getting available methods.")
            methods = await self._run_in_executor(self.chargefw2.get_available_methods)

            return methods
        except Exception as e:
            self.logger.error(f"Error getting available methods: {e}")
            raise e

    async def get_suitable_methods(self, file: UploadFile) -> list[dict]:
        """Get suitable methods for charge calculation based on the provided file."""

        workdir = self.io.create_tmp_dir("suitable-methods")
        new_file_path, _ = await self.io.store_upload_file(file, workdir)
        molecules = await self.read_molecules(new_file_path)

        try:
            self.logger.info(f"Getting suitable methods for file {file.filename}")
            suitable_methods = await self._run_in_executor(
                self.chargefw2.get_suitable_methods, molecules
            )

            # map from tuple to dictionary
            suitable_methods = [
                {"method": method, "parameters": parameters}
                for method, parameters in suitable_methods
            ]

            return suitable_methods
        except Exception as e:
            self.logger.error(f"Error getting suitable methods for file {file.filename}: {e}")
            raise e

    async def get_available_parameters(self, method: str) -> list[str]:
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
        self, file_path: str, read_hetatm: bool = True, ignore_water: bool = False
    ) -> Molecules:
        """Load molecules from a file"""
        try:
            self.logger.info(f"Loading molecules from file {file_path}.")
            molecules = await self._run_in_executor(
                self.chargefw2.molecules, file_path, read_hetatm, ignore_water
            )

            return molecules
        except Exception as e:
            self.logger.error(f"Error loading molecules from file {file_path}: {e}")
            raise e

    async def calculate_charges(
        self,
        files: list[UploadFile],
        config: ChargeCalculationConfig,
    ) -> list[CalculationDto]:
        """Calculate charges for provided files."""

        workdir = self.io.create_tmp_dir("calculations")
        semaphore = asyncio.Semaphore(4)  # limit to 4 concurrent calculations

        async def process_file(file: UploadFile) -> ChargeCalculationResult:
            async with semaphore:
                try:
                    new_file_path, file_hash = await self.io.store_upload_file(file, workdir)
                    existing_calculation = self.calculations_repository.get(
                        CalculationsFilters(
                            hash=file_hash,
                            method=config.method,
                            parameters=config.parameters,
                            read_hetatm=config.read_hetatm,
                            ignore_water=config.ignore_water,
                        )
                    )

                    if not existing_calculation:
                        self.logger.info(f"Calculating charges for file {file.filename}.")
                        molecules = await self.read_molecules(
                            new_file_path, config.read_hetatm, config.ignore_water
                        )
                        charges = await self._run_in_executor(
                            self.chargefw2.calculate_charges,
                            molecules,
                            config.method,
                            config.parameters,
                        )
                    else:
                        self.logger.info(
                            f"Skipping file {file.filename}. Charges already calculated."
                        )
                        charges = existing_calculation.charges

                    result = ChargeCalculationResult(
                        file=file.filename, file_hash=file_hash, charges=charges
                    )

                    if not existing_calculation:
                        new_calculation = self.calculations_repository.store(result, config)
                        result.id = new_calculation.id
                    else:
                        result.id = existing_calculation.id

                    return result
                except Exception as e:
                    self.logger.error(
                        f"Error calculating charges for file {file.filename}: {str(e)}"
                    )
                    return ChargeCalculationResult(file=file.filename, file_hash=file_hash)

        # Process all files concurrently, store to database and cleanup
        try:
            results = await asyncio.gather(
                *[process_file(file) for file in files], return_exceptions=True
            )
            return [CalculationDto.from_result(result, config) for result in results]
        finally:
            self.io.remove_tmp_dir(workdir)

    async def info(self, file: UploadFile) -> dict:
        """Get information about the provided file."""

        try:
            workdir = self.io.create_tmp_dir("info")
            new_file_path, _ = await self.io.store_upload_file(file, workdir)

            self.logger.info(f"Getting info for file {file.filename}.")
            molecules = await self.read_molecules(new_file_path)

            info = molecules.info()

            return info.to_dict()
        except Exception as e:
            self.logger.error(f"Error getting info for file {file.filename}: {str(e)}")
            raise e
        finally:
            self.io.remove_tmp_dir(workdir)

    def get_calculations(self, filters: PagingFilters) -> PagedList[CalculationDto]:
        """Get all calculations stored in the database."""

        try:
            self.logger.info("Getting all calculations.")
            calculations = self.calculations_repository.get_all(filters=filters)

            return calculations
        except Exception as e:
            self.logger.error(f"Error getting all calculations: {str(e)}")
            raise e
