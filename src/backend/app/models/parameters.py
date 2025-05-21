from dataclasses import dataclass


@dataclass(frozen=True)
class Parameters:
    """Parameters for charge calculation."""

    full_name: str
    internal_name: str
    publication: str
    method: str
