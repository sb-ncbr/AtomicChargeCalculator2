from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class AtomTypeCount(BaseModel):
    """Counts of atom types."""

    symbol: str
    count: int

    def __init__(self, type_counts: dict[str, Any]) -> None:
        super().__init__(symbol=type_counts.get("symbol", ""), count=type_counts.get("count", 0))

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class MoleculeSetStats(BaseModel):
    """Information about the molecules in the provided file."""

    total_molecules: int
    total_atoms: int
    atom_type_counts: list[AtomTypeCount]

    def __init__(self, info: dict[str, Any]) -> None:
        super().__init__(
            total_molecules=info.get("total_molecules", 0),
            total_atoms=info.get("total_atoms", 0),
            atom_type_counts=[AtomTypeCount(c) for c in info.get("atom_type_counts", [])],
        )

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
