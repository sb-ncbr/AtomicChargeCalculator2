"""Dependency injection container."""

import os

from dependency_injector import containers, providers
from dotenv import load_dotenv, find_dotenv

from core.logging.file_logger import FileLogger
from core.integrations.chargefw2.chargefw2 import ChargeFW2Local
from core.integrations.io.io import IOLocal

from db.database import Database, SessionManager
from db.repositories.calculation_config_repository import CalculationConfigRepository
from db.repositories.calculation_repository import CalculationRepository
from db.repositories.calculation_set_repository import CalculationSetRepository

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
    session_manager = providers.Singleton(
        SessionManager, session_factory=db.provided.session_factory
    )

    # repositories
    set_repository = providers.Factory(CalculationSetRepository, session_manager=session_manager)
    calculation_repository = providers.Factory(
        CalculationRepository, session_manager=session_manager, set_repository=set_repository
    )
    config_repository = providers.Factory(
        CalculationConfigRepository,
        session_manager=session_manager,
        set_repository=set_repository,
    )

    # services
    logger_service = providers.Singleton(FileLogger)
    io_service = providers.Singleton(IOService, logger=logger_service, io=io)
    chargefw2_service = providers.Singleton(
        ChargeFW2Service,
        chargefw2=chargefw2,
        logger=logger_service,
        io=io_service,
        set_repository=set_repository,
        calculation_repository=calculation_repository,
        config_repository=config_repository,
    )
