import os
import pathlib

from gemmi import cif

from api.v1.constants import CHARGES_OUTPUT_EXTENSION
from core.logging.base import LoggerBase
from core.models.calculation import CalculationResultDto

from services.io import IOService


class MmCIFService:
    """Service for handling mmCIF file operations."""

    def __init__(self, logger: LoggerBase, io: IOService):
        self.logger = logger
        self.io = io

    def write_to_mmcif(
        self, user_id: str | None, computation_id: str, calculations: list[CalculationResultDto]
    ) -> dict:
        """Write charges to mmcif files with names corresponding to the input molecules.

        Args:
            data (dict): Data to write
            calculations (list[ChargeCalculationResult]): List of calculations to write.

        Returns:
            dict: Dictionary with "molecules" and "configs" keys.
        """

        data = self._transform_calculation_data(calculations)

        configs = data["configs"]
        molecules = list(data["molecules"])
        for molecule in molecules:
            self._write_molecule_to_mmcif(user_id, computation_id, molecule, data)

        return {"molecules": molecules, "configs": configs}

    def get_molecule_mmcif(self, path: str, molecule: str | None) -> str:
        """Returns a mmcif file for the provided molecule in the provided computation.

        Args:
            computation_id (str): Computation id.
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

            return str(pathlib.Path(path) / molecules[0])

        path = str(pathlib.Path(path) / f"{molecule.lower()}{CHARGES_OUTPUT_EXTENSION}")
        if not self.io.path_exists(path):
            raise FileNotFoundError()

        return path

    def _transform_calculation_data(self, calculations: list[CalculationResultDto]) -> dict:
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

    def _write_molecule_to_mmcif(
        self, user_id: str | None, computation_id: str, molecule: str, data: dict
    ) -> str:
        configs = data["configs"]
        charges = data["molecules"][molecule]["charges"]

        charges_path = self.io.get_charges_path(computation_id, user_id)
        output_file_path = os.path.join(charges_path, f"{molecule.lower()}.fw2.cif")

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
