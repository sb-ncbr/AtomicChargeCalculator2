from fastapi import FastAPI
from api.v1.routes.charges import charges_router
from api.v1.routes.auth import auth_router
from api.v1.routes.protonation import protonation_router
from api.v1.routes.user import user_router
from api.v1.middleware.logging import LoggingMiddleware
from core.dependency_injection.container import Container
from dotenv import load_dotenv

PREFIX = "/api/v1"
load_dotenv()


def create_app() -> FastAPI:
    # Create DI container
    container = Container()

    # Create FastAPI app
    app = FastAPI()

    # Wire dependencies
    container.wire()

    # Add middleware
    app.add_middleware(LoggingMiddleware)

    # Add routers
    app.include_router(router=charges_router, prefix=PREFIX)
    app.include_router(router=auth_router, prefix=PREFIX)
    app.include_router(router=protonation_router, prefix=PREFIX)
    app.include_router(router=user_router, prefix=PREFIX)

    return app


app = create_app()
