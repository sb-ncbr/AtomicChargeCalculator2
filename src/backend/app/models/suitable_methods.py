from dataclasses import dataclass

from models.method import Method
from models.parameters import Parameters


@dataclass
class SuitableMethods:
    """Result of suitable methods calculation."""

    methods: list[Method]
    parameters: dict[str, list[Parameters]]
