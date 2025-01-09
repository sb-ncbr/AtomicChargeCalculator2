from api.v1.schemas.base_response import BaseResponseSchema


class Response[T](BaseResponseSchema):
    """Response schema for a single item."""

    data: T


class ResponseMultiple[T](BaseResponseSchema):
    """Response schema for multiple items."""

    data: list[T]
    total_count: int
    page: int = 1
    page_size: int = 10
