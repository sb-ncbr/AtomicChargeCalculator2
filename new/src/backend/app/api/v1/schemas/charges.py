from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from models.calculation import CalculationConfigDto
from models.setup import AdvancedSettingsDto


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class SuitableMethodsRequest(BaseRequestModel):
    file_hashes: list[str]
    permissive_types: bool = True


class StatsRequest(BaseRequestModel):
    file_hash: str


class BestParametersRequest(BaseRequestModel):
    method_name: str
    file_hash: str
    permissive_types: bool = True


class CalculateChargesRequest(BaseRequestModel):
    configs: list[CalculationConfigDto]
    file_hashes: list[str]
    settings: AdvancedSettingsDto | None = None
    computation_id: str | None = None


class SetupRequest(BaseRequestModel):
    file_hashes: list[str]
    settings: AdvancedSettingsDto | None
