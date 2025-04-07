"""Provides logging middleware for the application."""

from typing import Awaitable, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from api.v1.container import Container

from services.logging.base import LoggerBase

RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""

    def __init__(self, app):
        super().__init__(app)
        self.logger: LoggerBase = Container.logger_service()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        self.logger.info(message=f"Request: {request.method} {request.url}")

        response = await call_next(request)

        self.logger.info(message=f"Response status: {response.status_code}")

        return response
