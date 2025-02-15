"""Calculation models"""

from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from core.integrations.chargefw2.base import Charges
from core.models.paging import PagingFilters


@dataclass
class CalculationsFilters:
    """Filters for calculations retrieval"""

    hash: str
    method: str
    parameters: str | None = None
    read_hetatm: bool = True
    ignore_water: bool = False
    paging: PagingFilters = field(default_factory=lambda: PagingFilters(1, 10))


@dataclass
class ChargeCalculationConfig:
    """Configuration for charge calculation"""

    method: str | None
    parameters: str | None
    read_hetatm: bool = True
    ignore_water: bool = False
    permissive_types: bool = False


@dataclass
class ChargeCalculationPart:
    """Result of charge calculation for a single file."""

    file: str
    file_hash: str
    id: str | None = None
    charges: Charges | None = None


class CalculationDto(BaseModel):
    """Calculation data transfer object"""

    file: str
    charges: dict
    success: bool = True

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    @staticmethod
    def from_result(result: ChargeCalculationPart) -> "CalculationDto":
        """Create DTO from calculation result"""

        return CalculationDto(
            file=result.file,
            charges=result.charges,
            success=result.charges is not None,
        )


@dataclass
class ChargeCalculationResult:
    """Result of charge calculation"""

    config: ChargeCalculationConfig
    calculations: list[CalculationDto]
