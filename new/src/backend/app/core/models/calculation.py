"""Calculation models"""

from dataclasses import dataclass, field

from pydantic import UUID4, BaseModel, ConfigDict
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

    method: str
    parameters: str | None
    read_hetatm: bool = True
    ignore_water: bool = False


@dataclass
class ChargeCalculationResult:
    """Result of charge calculation"""

    file: str
    file_hash: str
    id: str | None = None
    charges: Charges | None = None


class CalculationDto(BaseModel):
    """Calculation data transfer object"""

    id: UUID4
    method: str
    parameters: str | None
    read_hetatm: bool
    ignore_water: bool
    charges: dict
    success: bool = True

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    @staticmethod
    def from_result(
        result: ChargeCalculationResult, config: ChargeCalculationConfig
    ) -> "CalculationDto":
        """Create DTO from calculation result"""

        return CalculationDto(
            id=result.id,
            method=config.method,
            parameters=config.parameters,
            read_hetatm=config.read_hetatm,
            ignore_water=config.ignore_water,
            charges=result.charges,
            success=result.charges is not None,
        )
