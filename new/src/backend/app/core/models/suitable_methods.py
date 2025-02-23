from dataclasses import dataclass

from core.models.method import Method
from core.models.parameters import Parameters


@dataclass
class SuitableMethods:
    """Result of suitable methods calculation."""

    methods: list[Method]
    parameters: dict[str, list[Parameters]]
