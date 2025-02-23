from dataclasses import dataclass


@dataclass
class Parameters:
    """Parameters for charge calculation."""

    name: str
    internal_name: str
    publication: str
