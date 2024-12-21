from dependency_injector import containers
from dependency_injector import providers

from core.logging.file_logger import FileLogger
from core.integrations.chargefw2.chargefw2 import ChargeFW2Local
from core.integrations.io.io import IOLocal
from services.chargefw2 import ChargeFW2Service
from services.io import IOService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["api", "core", "services"])

    # integrations
    chargefw2 = providers.Singleton(ChargeFW2Local)
    io = providers.Singleton(IOLocal)

    # services
    logger_service = providers.Singleton(FileLogger)
    io_service = providers.Singleton(IOService, logger=logger_service, io=io)
    chargefw2_service = providers.Singleton(ChargeFW2Service, chargefw2=chargefw2, logger=logger_service, io=io_service)
