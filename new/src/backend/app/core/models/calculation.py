"""Calculation models"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from core.models.paging import PagingFilters
from core.integrations.chargefw2.base import Charges

from core.models.molecule_info import MoleculeSetStats


@dataclass
class CalculationsFilters:
    """Filters for calculations retrieval"""

    hash: str
    method: str
    parameters: str | None = None
    read_hetatm: bool = True
    ignore_water: bool = False
    permissive_types: bool = False
    paging: PagingFilters = field(default_factory=lambda: PagingFilters(1, 10))


@dataclass
class ChargeCalculationConfig:
    """Configuration for charge calculation"""

    method: str | None
    parameters: str | None
    read_hetatm: bool = True
    ignore_water: bool = False
    permissive_types: bool = False


class CalculationDto(BaseModel):
    """Calculation data transfer object"""

    file: str
    file_hash: str
    info: MoleculeSetStats
    charges: Charges

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CalculationConfigDto(BaseModel):
    """Calculation configuration data transfer object"""

    method: str
    parameters: str | None
    read_hetatm: bool
    ignore_water: bool
    permissive_types: bool

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CalculationPreviewDto(BaseModel):
    """Calculation preview data transfer object"""

    file: str

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CalculationSetDto(BaseModel):
    """Calculation set data transfer object"""

    id: uuid.UUID
    calculations: list[CalculationDto]
    configs: list[CalculationConfigDto]

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CalculationSetPreviewDto(BaseModel):
    """Calculation set preview data transfer object"""

    id: uuid.UUID
    files: dict[str, MoleculeSetStats]
    configs: list[CalculationConfigDto]
    created_at: datetime

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


@dataclass
class ChargeCalculationResult:
    """Result of charge calculation"""

    config: ChargeCalculationConfig
    calculations: list[CalculationDto]
