"""Main module for the application."""

from typing import Tuple
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from api.v1.routes.web.charges import charges_router as web_charges_router
from api.v1.routes.web.auth import auth_router
from api.v1.routes.web.protonation import protonation_router
from api.v1.routes.web.user import user_router
from api.v1.routes.internal.charges import charges_router
from api.v1.middleware.logging import LoggingMiddleware
from api.v1.middleware.exceptions import http_exception_handler

from core.dependency_injection.container import Container


PREFIX = "/api/v1"
WEB_PREFIX = f"{PREFIX}/web"
load_dotenv()


def create_apps() -> Tuple[FastAPI, FastAPI]:
    """Creates FastAPI apps with routers and middleware."""

    # Create DI container
    container = Container()

    # Create database
    db = container.db()
    db.create_database()

    # Create FastAPI app
    web_app = FastAPI()
    internal_app = FastAPI()

    # Wire dependencies
    container.wire()

    # Add web middleware
    web_app.add_middleware(LoggingMiddleware)
    web_app.add_exception_handler(HTTPException, http_exception_handler)

    # Add internal middleware
    internal_app.add_middleware(LoggingMiddleware)
    internal_app.add_exception_handler(HTTPException, http_exception_handler)

    # Add web routers
    web_app.include_router(router=web_charges_router, prefix=WEB_PREFIX)
    web_app.include_router(router=auth_router, prefix=WEB_PREFIX)
    web_app.include_router(router=protonation_router, prefix=WEB_PREFIX)
    web_app.include_router(router=user_router, prefix=WEB_PREFIX)

    # Add internal routers
    internal_app.include_router(router=charges_router, prefix=PREFIX)

    return web_app, internal_app


web_app, internal_app = create_apps()
