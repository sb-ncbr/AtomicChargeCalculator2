"""Calculation models"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from models.paging import PagingFilters
from models.molecule_info import MoleculeSetStats

from integrations.chargefw2.base import Charges
from models.setup import AdvancedSettingsDto


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


class CalculationConfigDto(BaseModel):
    """Calculation configuration data transfer object"""

    method: str | None = None
    parameters: str | None = None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)
    __hash__ = object.__hash__


class CalculationDto(BaseModel):
    """Calculation data transfer object"""

    file: str
    file_hash: str
    charges: Charges
    config: CalculationConfigDto

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
    settings: AdvancedSettingsDto

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CalculationSetPreviewDto(BaseModel):
    """Calculation set preview data transfer object"""

    id: uuid.UUID
    files: dict[str, MoleculeSetStats]
    configs: list[CalculationConfigDto]
    settings: AdvancedSettingsDto
    created_at: datetime

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CalculationResultDto(BaseModel):
    """Result of charge calculation"""

    config: CalculationConfigDto
    calculations: list[CalculationDto]

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)
