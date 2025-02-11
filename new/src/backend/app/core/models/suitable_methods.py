from dataclasses import dataclass


@dataclass
class SuitableMethods:
    """Result of suitable methods calculation."""

    methods: list[str]
    parameters: dict[str, list[str]]
