import logging
import os
from core.logging.base import LoggerBase


class FileLogger(LoggerBase):
    def __init__(self) -> None:
        super().__init__()

        if not os.path.isdir("/tmp/atomic-logs"):
            os.mkdir("/tmp/atomic-logs")

        logging.basicConfig(
            filename="/tmp/atomic-logs/atomic-log.log",
            level=logging.INFO,
            filemode="a+",
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

        self.logger = logging.getLogger(__name__)

    def info(self, message: str) -> None:
        return self.logger.info(message)

    def warn(self, message: str) -> None:
        return self.logger.warning(message)

    def error(self, message: str) -> None:
        return self.logger.error(message)
