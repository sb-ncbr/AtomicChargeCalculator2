from api.v1.schemas.base import BaseSchema


class ResponseSingle[T](BaseSchema):
    data: T


class ResponseMultiple[T](BaseSchema):
    """Response schema for multiple items."""

    data: list[T]
    total_count: int
    page: int = 1
    page_size: int = 10
