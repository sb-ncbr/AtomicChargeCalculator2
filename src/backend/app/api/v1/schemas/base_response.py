"""Base response schema for all responses."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseResponseSchema(BaseModel):
    """Base schema. Also converts snake_case to camelCase property names."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
