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

    async def _run_in_executor(self, func, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)

    def get_available_methods(self) -> list[str]:
        return self.chargefw2.get_available_methods()

    async def get_suitable_methods(self, file: UploadFile) -> list[str]:
        workdir = self.io.create_tmp_dir("suitable-methods")
        new_file_path = await self.io.store_upload_file(file, workdir)
        molecules = await self.read_molecules(new_file_path)

        self.logger.info(f"Getting suitable methods for file {file.filename}")
        suitable_methods = self.chargefw2.get_suitable_methods(molecules)
        self.logger.info(f"Successfully got suitable methods for file {file.filename}")

        return suitable_methods

    def get_available_parameters(self, method: str) -> list[str]:
        return self.chargefw2.get_available_parameters(method)

    async def read_molecules(self, file_path: str, read_hetatm: bool = True, ignore_water: bool = False) -> Molecules:
        self.logger.info(f"Loading molecules from file {file_path}.")
        molecules = await self._run_in_executor(self.chargefw2.molecules, file_path, read_hetatm, ignore_water)
        self.logger.info(f"Successfully loaded molecules from file {file_path}.")

        return molecules

    async def calculate_charges(
        self,
        files: list[UploadFile],
        method_name: str,
        parameters_name: str | None = None,
        read_hetatm: bool = True,
        ignore_water: bool = False,
    ) -> list[ChargeCalculationResult]:
        workdir = self.io.create_tmp_dir("calculations")

        async def process_file(file: UploadFile):
            new_file_path = await self.io.store_upload_file(file, workdir)
            try:
                self.logger.info(f"Calculating charges for file {file.filename}.")

                molecules = await self.read_molecules(new_file_path, read_hetatm, ignore_water)
                charges = await self._run_in_executor(
                    self.chargefw2.calculate_charges, molecules, method_name, parameters_name
                )

                self.logger.info(f"Successfully calculated charges for file {file.filename}.")
                return ChargeCalculationResult(file=file.filename, charges=charges)
            except Exception as e:
                self.logger.error(f"Error calculating charges for file {file.filename}: {e}")
                return ChargeCalculationResult(file=file.filename, error=str(e))

        # Process all files concurrently
        results = await asyncio.gather(*[process_file(file) for file in files])
        return results

    async def info(self, file: UploadFile):
        workdir = self.io.create_tmp_dir("info")
        new_file_path = await self.io.store_upload_file(file, workdir)
        try:
            self.logger.info(f"Getting info for file {file.filename}.")
            molecules = await self.read_molecules(new_file_path)
            self.logger.info(f"Successfully got info for file {file.filename}.")

            return molecules.info().to_dict()
        except Exception as e:
            self.logger.error(f"Error getting info for file {file.filename}: {e}")
            return {"file": file.filename, "error": str(e)}
