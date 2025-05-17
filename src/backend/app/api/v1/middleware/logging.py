"""Provides logging middleware for the application."""

from datetime import timedelta
from timeit import default_timer as timer
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
        self.logger.info(
            message=f"Request from {request.client.host}: {request.method} {request.url}"
        )

        start = timer()
        response = await call_next(request)
        end = timer()

        self.logger.info(
            message=f"Response for {request.client.host}: {request.method} {request.url} finished with code {response.status_code} in {timedelta(seconds=end - start)}"
        )

        return response
