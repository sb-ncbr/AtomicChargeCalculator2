from abc import ABC, abstractmethod


class LoggerBase(ABC):
    """Service for logging"""

    @abstractmethod
    def info(self, message: str) -> None:
        """Logs the provided message with 'info' level.

        Args:
            message (str): Text to be logged.
        """
        raise NotImplementedError()

    @abstractmethod
    def warn(self, message: str) -> None:
        """Logs the provided message with 'warning' level.

        Args:
            message (str): _description_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    @abstractmethod
    def error(self, message: str) -> None:
        """Logs the provided message with 'info' level.

        Args:
            message (str): Text to be logged._
        """
        raise NotImplementedError()
