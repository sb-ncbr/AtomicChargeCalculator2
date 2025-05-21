"""ChargeFW2 service for a direct interaction (via bindings) with the ChargeFW2 framework."""

from typing import Dict
import chargefw2

from models.method import Method
from models.parameters import Parameters

from integrations.chargefw2.base import ChargeFW2Base


class ChargeFW2Local(ChargeFW2Base):
    """Service for a direct interaction (via bindings) with the ChargeFW2 framework."""

    def molecules(
        self,
        file_path: str,
        read_hetatm: bool = True,
        ignore_water: bool = False,
        permissive_types: bool = False,
    ) -> chargefw2.Molecules:
        """Load molecules from a file

        Args:
            file_path (str): Path from which to load molecules.
        Returns:
            chargefw2.Molecules: Parsed molecules
        """
        return chargefw2.Molecules(file_path, read_hetatm, ignore_water, permissive_types)

    def get_available_methods(self) -> list[Method]:
        """Get all available methods.

        Returns:
            list[str]: List of method names.
        """
        methods = chargefw2.get_available_methods()
        return [
            Method(
                internal_name=method.internal_name,
                name=method.name,
                full_name=method.full_name,
                publication=method.publication,
                type=method.type,
                has_parameters=method.has_parameters,
            )
            for method in methods
        ]

    def get_available_parameters(self, method: str) -> list[Parameters]:
        """Get all parameters available for provided method.

        Args:
            method (str): Method name.

        Returns:
            list[str]: List of parameter names.
        """
        parameters_list = chargefw2.get_available_parameters(method)
        return [
            Parameters(
                full_name=parameters.full_name,
                internal_name=parameters.internal_name,
                method=parameters.method,
                publication=parameters.publication,
            )
            for parameters in parameters_list
        ]

    def get_best_parameters(
        self, molecules: chargefw2.Molecules, method: str, permissive_types: bool
    ) -> Parameters | None:
        """Get best parameters for provided method.

        Args:
            method (str): Method name.
            molecules (chargefw2.Molecules): Set of molecules.
            permissive_types (bool): Use similar parameters for similar atom/bond types if no exact match is found.

        Returns:
            Parameters | None: Best Parameters for provided method.

        """
        parameters = chargefw2.get_best_parameters(molecules, method, permissive_types)

        if parameters is None:
            return None

        return Parameters(
            full_name=parameters.full_name,
            internal_name=parameters.internal_name,
            method=parameters.method,
            publication=parameters.publication,
        )

    def get_suitable_methods(
        self, molecules: chargefw2.Molecules
    ) -> list[tuple[Method, list[Parameters]]]:
        """Get methods and parameters that are suitable for a given set of molecules.

        Args:
            molecules (chargefw2.Molecules): Set of molecules.

        Returns:
            list[tuple[str, list[str]]]: List of tuples containing method name and parameters for that method.
        """

        suitable = chargefw2.get_suitable_methods(molecules)
        result = []
        for method, parameters_list in suitable:
            method_obj = Method(
                internal_name=method.internal_name,
                full_name=method.full_name,
                name=method.name,
                publication=method.publication,
                type=method.type,
                has_parameters=method.has_parameters,
            )
            parameters_obj = [
                Parameters(
                    full_name=parameters.full_name,
                    internal_name=parameters.internal_name,
                    method=parameters.method,
                    publication=parameters.publication,
                )
                for parameters in parameters_list
            ]
            result.append((method_obj, parameters_obj))

        return result

    def calculate_charges(
        self,
        molecules: chargefw2.Molecules,
        method_name: str,
        parameters_name: str | None = None,
        chg_out_dir: str = ".",
    ) -> Dict[str, list[float]]:
        """Calculate partial atomic charges for a given molecules and method.

        Args:
            molecules (chargefw2.Molecules): Set of molecules.
            method_name (str): Method name to be used.
            parameters_name (Optional[str], optional): Parameters to be used with provided method. Defaults to None.

        Returns:
            Dict[str, list[float]]: Dictionary with molecule names as keys and list of charges (floats) as values.
        """
        return chargefw2.calculate_charges(molecules, method_name, parameters_name, chg_out_dir)

    def save_charges(
        self,
        charges: Dict[str, list[float]],
        molecules: chargefw2.Molecules,
        method_name: str,
        parameters_name: str | None = None,
        chg_out_dir: str | None = None,
    ) -> None:
        """Save charges for a given molecules and method.

        Args:
            charges (Dict[str, list[float]]): Dictionary with molecule names as keys and list of charges (floats) as values.
            molecules (chargefw2.Molecules): Set of molecules.
            method_name (str): Method name to be used.
            parameters_name (Optional[str], optional): Parameters to be used with provided method. Defaults to None.
            chg_out_dir (Optional[str], optional): Path to the directory where to save the charges. Defaults to current working directory.
        """
        chargefw2.save_charges(charges, molecules, method_name, parameters_name, chg_out_dir)
