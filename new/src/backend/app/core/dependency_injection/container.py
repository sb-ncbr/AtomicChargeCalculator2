from dependency_injector import containers
from dependency_injector import providers

from core.logging.file_logger import FileLogger
from core.integrations.chargefw2.chargefw2 import ChargeFW2Local


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["api", "core", "services"])

    logger_service = providers.Singleton(FileLogger)
    chargefw2 = providers.Singleton(ChargeFW2Local)
