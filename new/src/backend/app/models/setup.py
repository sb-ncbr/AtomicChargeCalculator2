from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Setup(BaseModel):
    """Setup model."""

    computation_id: str


class AdvancedSettingsDto(BaseModel):
    """SetupSettings model."""

    read_hetatm: bool = True
    ignore_water: bool = False
    permissive_types: bool = True

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class SetupConfigDto(BaseModel):
    """SetupConfigDto model."""

    file_hashes: list[str]
    settings: AdvancedSettingsDto | None
