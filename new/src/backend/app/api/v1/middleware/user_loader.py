"""Provides user loader middleware for the application."""

from typing import Awaitable, Callable


from api.v1.container import Container
from db.repositories.user_repository import UserRepository
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from services.logging.base import LoggerBase
from services.oidc import OIDCService

RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


class UserLoaderMiddleware(BaseHTTPMiddleware):
    """Middleware used for
    1. verifying token
    2. loading user from the database
    3. setting it to the request state."""

    def __init__(self, app):
        super().__init__(app)
        self.logger: LoggerBase = Container.logger_service()
        self.oidc_service: OIDCService = Container.oidc_service()
        self.user_repository: UserRepository = Container.user_repository()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.user = None
        cookie = request.cookies.get("access_token")

        if cookie:
            payload = await self.oidc_service.verify_token(cookie)
            if payload:
                openid = payload["sub"]
                self.logger.info(f"Request contains valid token, loading user {openid}.")
                user = self.user_repository.get(openid)
                request.state.user = user

        # openid = "f8e916e578ec64cbb26786c2769b4a95bd87aef0@lifescience-ri.eu"
        # user = self.user_repository.get(openid)
        # request.state.user = user

        response = await call_next(request)
        return response
