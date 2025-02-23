"""ChargeFW2 service module."""

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from gemmi import cif

import asyncio
import os
import uuid

from fastapi import UploadFile

# Temporary solution to get Molecules class
from chargefw2 import Molecules

from core.integrations.chargefw2.base import ChargeFW2Base
from core.logging.base import LoggerBase
from core.models.calculation import (
    CalculationDto,
    ChargeCalculationConfig,
    ChargeCalculationPart,
    ChargeCalculationResult,
)
from core.models.molecule_info import MoleculeInfo
from core.models.paging import PagingFilters, PagedList
from core.models.suitable_methods import SuitableMethods

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

    def get_available_methods(self) -> list[str]:
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

            return SuitableMethods(methods=methods, parameters=parameters)
        except Exception as e:
            self.logger.error(
                f"Error getting suitable methods for computation id '{computation_id}': {e}"
            )
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

    # TODO: Remove
    # async def calculate_charges_old(
    #     self,
    #     files: list[UploadFile],
    #     config: ChargeCalculationConfig,
    # ) -> list[CalculationDto]:
    #     """Calculate charges for provided files."""

    #     workdir = self.io.create_tmp_dir("calculations")
    #     semaphore = asyncio.Semaphore(4)  # limit to 4 concurrent calculations

    #     async def process_file(file: UploadFile) -> ChargeCalculationPart:
    #         async with semaphore:
    #             try:
    #                 new_file_path, file_hash = await self.io.store_upload_file(file, workdir)
    #                 existing_calculation = self.calculations_repository.get(
    #                     CalculationsFilters(
    #                         hash=file_hash,
    #                         method=config.method,
    #                         parameters=config.parameters,
    #                         read_hetatm=config.read_hetatm,
    #                         ignore_water=config.ignore_water,
    #                     )
    #                 )

    #                 if not existing_calculation:
    #                     self.logger.info(f"Calculating charges for file {file.filename}.")
    #                     molecules = await self.read_molecules(
    #                         new_file_path, config.read_hetatm, config.ignore_water
    #                     )
    #                     charges = await self._run_in_executor(
    #                         self.chargefw2.calculate_charges,
    #                         molecules,
    #                         config.method,
    #                         config.parameters,
    #                     )
    #                 else:
    #                     self.logger.info(
    #                         f"Skipping file {file.filename}. Charges already calculated."
    #                     )
    #                     charges = existing_calculation.charges

    #                 result = ChargeCalculationPart(
    #                     file=file.filename, file_hash=file_hash, charges=charges
    #                 )

    #                 if not existing_calculation:
    #                     new_calculation = self.calculations_repository.store(result, config)
    #                     result.id = new_calculation.id
    #                 else:
    #                     result.id = existing_calculation.id

    #                 return result
    #             except Exception as e:
    #                 self.logger.error(
    #                     f"Error calculating charges for file {file.filename}: {str(e)}"
    #                 )
    #                 return ChargeCalculationPart(file=file.filename, file_hash=file_hash)

    #     # Process all files concurrently, store to database and cleanup
    #     try:
    #         results = await asyncio.gather(
    #             *[process_file(file) for file in files], return_exceptions=True
    #         )
    #         return [CalculationDto.from_result(result) for result in results]
    #     finally:
    #         self.io.remove_tmp_dir(workdir)

    async def calculate_charges(
        self, computation_id: str, config: ChargeCalculationConfig
    ) -> ChargeCalculationResult:
        """Calculate charges for provided files."""

        workdir = self.io.get_input_path(computation_id)
        charges_dir = self.io.get_charges_path(computation_id)
        self.io.create_tmp_dir(charges_dir)

        semaphore = asyncio.Semaphore(4)  # limit to 4 concurrent calculations

        async def process_file(file: str) -> ChargeCalculationPart:
            full_path = os.path.join(workdir, file)
            async with semaphore:
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
                result = ChargeCalculationPart(
                    id=str(uuid.uuid4()),
                    file=file.split("_", 1)[-1],
                    file_hash=file.split("_", 1)[0],
                    charges=charges,
                )
                return result

        try:
            if not config.method:
                # No method provided -> use most suitable method and parameters
                suitable = await self.get_suitable_methods(computation_id)
                config.method = suitable.methods[0]
                parameters: list[str] = suitable.parameters.get(config.method, [])
                config.parameters = (
                    parameters[0].replace(".json", "") if len(parameters) > 0 else None
                )
                self.logger.info(
                    f"""No method provided. 
                        Using method '{config.method}' with parameters '{config.parameters}'."""
                )

            # Process all files concurrently
            inputs = self.io.listdir(workdir)
            results = await asyncio.gather(
                *[process_file(file) for file in inputs],
                return_exceptions=True,
            )
            # Filter out exceptions
            calculations = [
                CalculationDto.from_result(result)
                for result in results
                if isinstance(result, CalculationDto)
            ]
            return ChargeCalculationResult(
                config=config,
                calculations=calculations,
            )
        except Exception as e:
            self.logger.error(f"Error calculating charges: {str(e)}")
            raise e

    # TODO: Refactor. Move closures somewhere else?
    def write_to_mmcif(
        self, computation_id: str, calculations: list[ChargeCalculationResult]
    ) -> dict:
        """Write charges to mmcif files with names corresponding to the input molecules.

        Args:
            data (dict): Data to write
            calculations (list[ChargeCalculationResult]): List of calculations to write.

        Returns:
            dict: Dictionary with "molecules" and "configs" keys.
        """

        def transform_data() -> dict:
            """Transforms input data to a 'molecule-focused' format"""
            transformed = {
                "molecules": {},
                "configs": [
                    {
                        "method": calculation.config.method,
                        "parameters": calculation.config.parameters,
                    }
                    for calculation in calculations
                ],
            }

            for calculation in calculations:
                for calculation_part in calculation.calculations:
                    if not calculation_part.success:
                        continue

                    for molecule, charges in calculation_part.charges.items():
                        if molecule not in transformed["molecules"]:
                            transformed["molecules"][molecule] = {"charges": []}

                        transformed["molecules"][molecule]["charges"].append(charges)

            return transformed

        def write(molecule: str, data: dict) -> str:
            configs = data["configs"]
            charges = data["molecules"][molecule]["charges"]

            output_file_path = os.path.join(
                self.io.get_charges_path(computation_id), f"{molecule.lower()}.fw2.cif"
            )

            document = cif.read_file(output_file_path)
            block = document.sole_block()

            sb_ncbr_partial_atomic_charges_meta_prefix = "_sb_ncbr_partial_atomic_charges_meta."
            sb_ncbr_partial_atomic_charges_prefix = "_sb_ncbr_partial_atomic_charges."
            sb_ncbr_partial_atomic_charges_meta_attributes = ["id", "type", "method"]
            sb_ncbr_partial_atomic_charges_attributes = ["type_id", "atom_id", "charge"]

            block.find_mmcif_category(sb_ncbr_partial_atomic_charges_meta_prefix).erase()
            block.find_mmcif_category(sb_ncbr_partial_atomic_charges_prefix).erase()

            metadata_loop = block.init_loop(
                sb_ncbr_partial_atomic_charges_meta_prefix,
                sb_ncbr_partial_atomic_charges_meta_attributes,
            )

            for type_id, config in enumerate(configs):
                method_name = config["method"]
                parameters_name = config["parameters"]
                metadata_loop.add_row(
                    [f"{type_id + 1}", "'empirical'", f"'{method_name}/{parameters_name}'"]
                )

            charges_loop = block.init_loop(
                sb_ncbr_partial_atomic_charges_prefix, sb_ncbr_partial_atomic_charges_attributes
            )

            for type_id, charges in enumerate(charges):
                for atom_id, charge in enumerate(charges):
                    charges_loop.add_row([f"{type_id + 1}", f"{atom_id + 1}", f"{charge: .4f}"])

            block.write_file(output_file_path)

        data = transform_data()

        configs = data["configs"]
        molecules = list(data["molecules"])
        for molecule in molecules:
            write(molecule, data)

        return {"molecules": molecules, "configs": configs}

    async def info(self, file: UploadFile) -> MoleculeInfo:
        """Get information about the provided file."""

        try:
            workdir = self.io.create_tmp_dir("info")
            new_file_path, _ = await self.io.store_upload_file(file, workdir)

            self.logger.info(f"Getting info for file {file.filename}.")
            molecules = await self.read_molecules(new_file_path)

            info = molecules.info()

            return MoleculeInfo(info.to_dict())
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
