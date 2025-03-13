"""ChargeFW2 service module."""

import asyncio
import os
import traceback

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

from gemmi import cif

from fastapi import UploadFile

# Temporary solution to get Molecules class
from chargefw2 import Molecules

from core.integrations.chargefw2.base import ChargeFW2Base
from core.logging.base import LoggerBase
from core.models.calculation import (
    CalculationConfigDto,
    CalculationDto,
    CalculationSetDto,
    CalculationSetPreviewDto,
    CalculationsFilters,
    ChargeCalculationConfig,
    ChargeCalculationResult,
)
from core.models.molecule_info import MoleculeSetStats
from core.models.method import Method
from core.models.paging import PagedList
from core.models.parameters import Parameters
from core.models.suitable_methods import SuitableMethods


from api.v1.constants import CHARGES_OUTPUT_EXTENSION

from db.models.calculation.calculation import Calculation
from db.models.calculation.calculation_config import CalculationConfig
from db.models.calculation.calculation_set import CalculationSet

from db.repositories.calculation_set_repository import (
    CalculationSetRepository,
    CalculationSetFilters,
)
from db.repositories.calculation_config_repository import CalculationConfigRepository
from db.repositories.calculation_repository import CalculationRepository

from services.io import IOService


class ChargeFW2Service:
    """ChargeFW2 service."""

    def __init__(
        self,
        chargefw2: ChargeFW2Base,
        logger: LoggerBase,
        io: IOService,
        set_repository: CalculationSetRepository,
        calculation_repository: CalculationRepository,
        config_repository: CalculationConfigRepository,
        max_workers: int = 4,
    ):
        self.chargefw2 = chargefw2
        self.logger = logger
        self.io = io
        self.set_repository = set_repository
        self.calculation_repository = calculation_repository
        self.config_repository = config_repository
        self.executor = ThreadPoolExecutor(max_workers)

    async def _run_in_executor(self, func, *args, executor=None):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor if executor is None else executor, func, *args
        )

    def get_available_methods(self) -> list[Method]:
        """Get available methods for charge calculation."""

        try:
            self.logger.info("Getting available methods.")
            methods = self.chargefw2.get_available_methods()

            return methods
        except Exception as e:
            self.logger.error(f"Error getting available methods: {e}")
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

            # Add metadata to methods and paremeters
            all_methods_with_metadata = self.get_available_methods()
            methods_with_metadata = [
                m for m in all_methods_with_metadata if m.internal_name in methods
            ]
            parameters_with_metadata = {
                method: [Parameters(**(await self.get_parameters_metadata(p))) for p in params]
                for method, params in parameters.items()
            }
            return SuitableMethods(
                methods=methods_with_metadata, parameters=parameters_with_metadata
            )
        except Exception as e:
            self.logger.error(
                f"Error getting suitable methods for computation id '{computation_id}': {e}"
            )
            raise e

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
    ) -> ChargeCalculationResult:
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
                exists = self.get_calculation(
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

                self.calculation_repository.store(
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
            return ChargeCalculationResult(
                config=ChargeCalculationConfig(
                    method=config.method,
                    parameters=config.parameters,
                    read_hetatm=config.read_hetatm,
                    ignore_water=config.ignore_water,
                    permissive_types=config.permissive_types,
                ),
                calculations=calculations,
            )
        except Exception as e:
            self.logger.error(f"Error calculating charges: {traceback.format_exc()}")
            raise e

    async def calculate_charges_multi(
        self, computation_id: str, configs: list[ChargeCalculationConfig]
    ) -> list[ChargeCalculationResult]:
        """Calculate charges for provided files.

        Args:
            computation_id (str): Computation id
            configs (list[ChargeCalculationConfig]): List of configurations.

        Returns:
            ChargeCalculationResult: List of successful calculations. Failed calculations are skipped.
        """

        async def process_config(config: ChargeCalculationConfig) -> ChargeCalculationResult:
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
            db_config = self.config_repository.store(
                CalculationConfig(set_id=computation_id, **asdict(config))
            )
            return await self.calculate_charges(computation_id, db_config)

        calculations = await asyncio.gather(*[process_config(config) for config in configs])
        _ = self.write_to_mmcif(computation_id, calculations)

        return calculations

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

    def store_calculation_set(
        self, computation_id: str, data: list[ChargeCalculationResult]
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
                id=computation_id, calculations=calculations, configs=configs
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

    def get_molecule_mmcif(self, path: str, molecule: str | None) -> str:
        """Returns a mmcif file for the provided molecule in the provided path.

        Args:
            path (str): Path to computation results.
            molecule (str | None): Molecule name. Will return the first one if not provided.

        Raises:
            FileNotFoundError: If the provided path or molecule does not exist.

        Returns:
            str: Path to the mmcif file.
        """
        if not self.io.path_exists(path):
            raise FileNotFoundError()

        if molecule is None:
            molecules = [
                file for file in self.io.listdir(path) if file.endswith(CHARGES_OUTPUT_EXTENSION)
            ]

            if len(molecules) == 0:
                raise FileNotFoundError()

            return os.path.join(path, molecules[0])

        path = os.path.join(path, molecule.lower() + CHARGES_OUTPUT_EXTENSION)
        if not self.io.path_exists(path):
            raise FileNotFoundError()

        return path

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
