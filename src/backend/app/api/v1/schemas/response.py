"""Response schemas for API endpoints."""

from api.v1.schemas.base_response import BaseResponseSchema


class Response[T](BaseResponseSchema):
    """Response schema for a single item."""

    success: bool = True
    data: T


class ResponseError(BaseResponseSchema):
    """Response schema for errors."""

    success: bool = False
    message: str
