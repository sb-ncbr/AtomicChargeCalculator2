"""Provides exception handlers for HTTP exceptions."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from api.v1.schemas.response import ResponseError


async def http_exception_handler(_: Request, exception: HTTPException):
    """Handle HTTP exceptions and return a JSON response with the error message."""
    return JSONResponse(
        status_code=exception.status_code,
        content=ResponseError(message=exception.detail).model_dump(),
    )
