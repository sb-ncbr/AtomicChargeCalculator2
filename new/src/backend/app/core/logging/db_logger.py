from core.logging.base import LoggerBase


class DBLogger(LoggerBase):
    def __init__(self) -> None:
        super().__init__()

    def info(self, message) -> None:
        raise NotImplementedError()

    def warn(self, message) -> None:
        raise NotImplementedError()

    def error(self, message) -> None:
        raise NotImplementedError()
