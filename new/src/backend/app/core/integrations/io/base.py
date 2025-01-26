"""Base class for the file system interaction service."""

from abc import ABC, abstractmethod


class IOBase(ABC):
    """Service for interaction with the file system."""

    @abstractmethod
    def create_tmp_dir(self, name: str = "") -> str:
        """Creates temporary directory.

        Returns:
                str: Path to te created temporary directory.
        """
        raise NotImplementedError()

    @abstractmethod
    def remove_tmp_dir(self, path: str) -> None:
        """Removes temporary directory.

        Args:
            name (str): Path to the temporary directory which will be removed.
        """
        raise NotImplementedError()

    @abstractmethod
    def cp(self, path_src: str, path_dst: str) -> str:
        """Copies file from 'path_src' to 'path_dst'.

        Args:
            path_src (str): Location of a file to copy.
            path_dst (str): Where to copy the file.

        Returns:
            bool: True if the operation was successful, otherwise False.
        """
        raise NotImplementedError()
