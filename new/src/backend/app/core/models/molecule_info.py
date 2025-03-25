from dataclasses import dataclass
from typing import Any


@dataclass
class AtomTypeCount:
    """Counts of atom types."""

    symbol: str
    count: int

    def __init__(self, type_counts: dict[str, Any]) -> None:
        self.symbol = type_counts.get("symbol", "")
        self.count = type_counts.get("count", 0)


@dataclass
class MoleculeSetStats:
    """Information about the molecules in the provided file."""

    total_molecules: int
    total_atoms: int
    atom_type_counts: list[AtomTypeCount]

    def __init__(self, info: dict[str, Any]) -> None:
        self.total_molecules = info.get("total_molecules", 0)
        self.total_atoms = info.get("total_atoms", 0)
        self.atom_type_counts = [AtomTypeCount(c) for c in info.get("atom_type_counts", [])]
