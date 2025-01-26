"""Custom HTTP exceptions for the application."""

from typing import Any
from fastapi import HTTPException


class BadRequestError(HTTPException):
    """Exception for 400 Bad Request errors."""

    def __init__(
        self, status_code: int, detail: str, headers: dict[str, Any] | None = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
