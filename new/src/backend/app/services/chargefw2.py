import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from fastapi import UploadFile

# Temporary solution to get Molecules class
from chargefw2 import Molecules

from core.integrations.chargefw2.base import ChargeFW2Base, Charges
from core.logging.base import LoggerBase
from services.io import IOService


@dataclass
class ChargeCalculationResult:
    file: str
    charges: Charges | None = None
    error: str | None = None


class ChargeFW2Service:
    def __init__(self, chargefw2: ChargeFW2Base, logger: LoggerBase, io: IOService, max_workers: int = 4):
        self.chargefw2 = chargefw2
        self.logger = logger
        self.io = io
        self.executor = ThreadPoolExecutor(max_workers)

    async def _run_in_executor(self, func, *args, executor=None):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor if executor is None else executor, func, *args)

    async def get_available_methods(self) -> list[str]:
        try:
            self.logger.info("Getting available methods.")
            methods = await self._run_in_executor(self.chargefw2.get_available_methods)
            self.logger.info("Successfully got available methods.")

            return methods
        except Exception as e:
            self.logger.error(f"Error getting available methods: {e}")
            raise e

    async def get_suitable_methods(self, file: UploadFile) -> list[str]:
        workdir = self.io.create_tmp_dir("suitable-methods")
        new_file_path = await self.io.store_upload_file(file, workdir)
        molecules = await self.read_molecules(new_file_path)

        try:
            self.logger.info(f"Getting suitable methods for file {file.filename}")
            suitable_methods = await self._run_in_executor(self.chargefw2.get_suitable_methods, molecules)
            self.logger.info(f"Successfully got suitable methods for file {file.filename}")

            return suitable_methods
        except Exception as e:
            self.logger.error(f"Error getting suitable methods for file {file.filename}: {e}")
            raise e

    async def get_available_parameters(self, method: str) -> list[str]:
        try:
            self.logger.info(f"Getting available parameters for method {method}.")
            parameters = await self._run_in_executor(self.chargefw2.get_available_parameters, method)
            self.logger.info(f"Successfully got available parameters for method {method}.")

            return parameters
        except Exception as e:
            self.logger.error(f"Error getting available parameters for method {method}: {e}")
            raise e

    async def read_molecules(self, file_path: str, read_hetatm: bool = True, ignore_water: bool = False) -> Molecules:
        try:
            self.logger.info(f"Loading molecules from file {file_path}.")
            molecules = await self._run_in_executor(self.chargefw2.molecules, file_path, read_hetatm, ignore_water)
            self.logger.info(f"Successfully loaded molecules from file {file_path}.")

            return molecules
        except Exception as e:
            self.logger.error(f"Error loading molecules from file {file_path}: {e}")
            raise e

    async def calculate_charges(
        self,
        files: list[UploadFile],
        method_name: str,
        parameters_name: str | None = None,
        read_hetatm: bool = True,
        ignore_water: bool = False,
    ) -> list[ChargeCalculationResult]:
        workdir = self.io.create_tmp_dir("calculations")
        semaphore = asyncio.Semaphore(4)  # limit to 4 concurrent calculations

        async def process_file(file: UploadFile):
            async with semaphore:
                try:
                    new_file_path = await self.io.store_upload_file(file, workdir)
                    molecules = await self.read_molecules(new_file_path, read_hetatm, ignore_water)

                    self.logger.info(f"Calculating charges for file {file.filename}.")
                    charges = await self._run_in_executor(
                        self.chargefw2.calculate_charges, molecules, method_name, parameters_name
                    )
                    self.logger.info(f"Successfully calculated charges for file {file.filename}.")

                    return ChargeCalculationResult(file=file.filename, charges=charges)
                except Exception as e:
                    self.logger.error(f"Error calculating charges for file {file.filename}: {e}, {e.__class__}")
                    return ChargeCalculationResult(file=file.filename, error=str(e))

        # Process all files concurrently and cleanup
        try:
            results = await asyncio.gather(*[process_file(file) for file in files])
        finally:
            self.io.remove_tmp_dir(workdir)

        return results

    async def info(self, file: UploadFile) -> dict:
        workdir = self.io.create_tmp_dir("info")
        try:
            new_file_path = await self.io.store_upload_file(file, workdir)
            self.logger.info(f"Getting info for file {file.filename}.")
            molecules = await self.read_molecules(new_file_path)

            info = molecules.info()
            self.logger.info(f"Successfully got info for file {file.filename}.")

            return info.to_dict()
        except Exception as e:
            self.logger.error(f"Error getting info for file {file.filename}: {e}")
            raise e
        finally:
            self.io.remove_tmp_dir(workdir)
