from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.json_schema import SkipJsonSchema

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

    # exclude computation_id from docs
    computation_id: SkipJsonSchema[str | None] = Field(None, exclude=True)


class SetupRequest(BaseRequestModel):
    file_hashes: list[str]
    settings: AdvancedSettingsDto | None
