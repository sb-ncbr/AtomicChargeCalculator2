from typing import Dict, Optional
import chargefw2

from core.integrations.chargefw2.base import ChargeFW2Base


class ChargeFW2Local(ChargeFW2Base):
    """Service for a direct interaction (via bindings) with the ChargeFW2 framework."""

    def molecules(self, file_path: str, read_hetatm: bool = True, ignore_water: bool = False) -> chargefw2.Molecules:
        """Load molecules from a file

        Args:
            file_path (str): Path from which to load molecules.
        Returns:
            chargefw2.Molecules: Parsed molecules
        """
        return chargefw2.Molecules(file_path, read_hetatm, ignore_water)

    def get_available_methods(self) -> list[str]:
        """Get all available methods.

        Returns:
            list[str]: List of method names.
        """
        return chargefw2.get_available_methods()

    def get_available_parameters(self, method: str) -> list[str]:
        """Get all parameters available for provided method.

        Args:
            method (str): Method name.

        Returns:
            list[str]: List of parameter names.
        """
        return chargefw2.get_available_parameters(method)

    def get_suitable_methods(self, molecules: chargefw2.Molecules) -> list[tuple[str, list[str]]]:
        """Get methods and parameters that are suitable for a given set of molecules.

        Args:
            molecules (chargefw2.Molecules): Set of molecules.

        Returns:
            list[tuple[str, list[str]]]: List of tuples containing method name and parameters for that method.
        """
        return chargefw2.get_suitable_methods(molecules)

    def calculate_charges(
        self,
        molecules: chargefw2.Molecules,
        method_name: str,
        parameters_name: Optional[str] = None,
    ) -> Dict[str, list[float]]:
        """Calculate partial atomic charges for a given molecules and method.

        Args:
            molecules (chargefw2.Molecules): Set of molecules.
            method_name (str): Method name to be used.
            parameters_name (Optional[str], optional): Parameters to be used with provided method. Defaults to None.

        Returns:
            Dict[str, list[float]]: Dictionary with molecule names as keys and list of charges (floats) as values.
        """
        return chargefw2.calculate_charges(molecules, method_name, parameters_name)
