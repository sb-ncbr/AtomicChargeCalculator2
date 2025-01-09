from typing import Tuple
from fastapi import FastAPI
from api.v1.routes.web.charges import charges_router as web_charges_router
from api.v1.routes.web.auth import auth_router
from api.v1.routes.web.protonation import protonation_router
from api.v1.routes.web.user import user_router
from api.v1.routes.internal.charges import charges_router
from api.v1.middleware.logging import LoggingMiddleware
from core.dependency_injection.container import Container
from dotenv import load_dotenv

PREFIX = "/api/v1"
WEB_PREFIX = f"{PREFIX}/web"
load_dotenv()


def create_apps() -> Tuple[FastAPI, FastAPI]:
    # Create DI container
    container = Container()

    # Create FastAPI app
    web_app = FastAPI()
    internal_app = FastAPI()

    # Wire dependencies
    container.wire()

    # Add web middleware
    web_app.add_middleware(LoggingMiddleware)

    # Add internal middleware
    internal_app.add_middleware(LoggingMiddleware)

    # Add web routers
    web_app.include_router(router=web_charges_router, prefix=WEB_PREFIX)
    web_app.include_router(router=auth_router, prefix=WEB_PREFIX)
    web_app.include_router(router=protonation_router, prefix=WEB_PREFIX)
    web_app.include_router(router=user_router, prefix=WEB_PREFIX)

    # Add internal routers
    internal_app.include_router(router=charges_router, prefix=PREFIX)

    return web_app, internal_app


web_app, internal_app = create_apps()
