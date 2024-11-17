from typing import Awaitable, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from core.logging.base import LoggerBase
from core.dependency_injection.container import Container

RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger: LoggerBase = Container.logger_service()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        self.logger.info(message=f"Request: {request.method} {request.url}")

        response = await call_next(request)

        self.logger.info(message=f"Response status: {response.status_code}")

        return response
