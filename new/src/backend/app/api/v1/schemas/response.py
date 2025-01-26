"""Response schemas for API endpoints."""

from api.v1.schemas.base_response import BaseResponseSchema


class Response[T](BaseResponseSchema):
    """Response schema for a single item."""

    success: bool = True
    status_code: int = 200
    data: T


class ResponseError(BaseResponseSchema):
    """Response schema for errors."""

    success: bool = False
    message: str
    status_code: int = 400
