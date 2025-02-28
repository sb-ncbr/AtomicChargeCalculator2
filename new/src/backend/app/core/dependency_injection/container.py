"""Dependency injection container."""

import os

from dependency_injector import containers, providers
from dotenv import load_dotenv, find_dotenv

from core.logging.file_logger import FileLogger
from core.integrations.chargefw2.chargefw2 import ChargeFW2Local
from core.integrations.io.io import IOLocal

from db.database import Database
from db.repositories.calculations_repository import CalculationsRepository

from services.chargefw2 import ChargeFW2Service
from services.io import IOService


load_dotenv(find_dotenv())


class Container(containers.DeclarativeContainer):
    """IoC container for the application."""

    wiring_config = containers.WiringConfiguration(packages=["api", "core", "services"])

    # integrations
    chargefw2 = providers.Singleton(ChargeFW2Local)
    io = providers.Singleton(IOLocal)

    # database
    db = providers.Singleton(Database, db_url=os.environ.get("ACC2_DB_URL"))

    # repositories
    calculations_repository = providers.Factory(
        CalculationsRepository, session_factory=db.provided.session
    )

    # services
    logger_service = providers.Singleton(FileLogger)
    io_service = providers.Singleton(IOService, logger=logger_service, io=io)
    chargefw2_service = providers.Singleton(
        ChargeFW2Service,
        chargefw2=chargefw2,
        logger=logger_service,
        io=io_service,
        calculations_repository=calculations_repository,
    )
