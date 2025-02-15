"""Base class for the file system interaction service."""

from abc import ABC, abstractmethod
import os
import uuid

from fastapi import UploadFile


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

    @abstractmethod
    def listdir(self, directory: str = ".") -> list[str]:
        """Lists contents of the provided directory.

        Args:
            directory (str): Directory to list.

        Returns:
            str: List containing the names of the entries in the provided directory.
        """
        raise NotImplementedError()

    @abstractmethod
    async def store_upload_file(self, file: UploadFile, directory: str) -> tuple[str, str]:
        """Stores the provided file on disk.

        Args:
            file (UploadFile): File to be stored.
            directory (str): Path to an existing directory.

        Returns:
            tuple[str, str]: Tuple containing path to the file and hash of the file contents.
        """
        raise NotImplementedError()

    @abstractmethod
    def path_exists(self, path: str) -> bool:
        """Check if the provided path exists.

        Args:
            path (str): Path to verify.

        Returns:
            bool: True if the path exists, otherwise False.
        """
        raise NotImplementedError()

    @staticmethod
    def get_unique_filename(filename: str) -> str:
        """Generate unique filename."""

        base, ext = os.path.splitext(filename)
        return f"{str(uuid.uuid4())}_{base}{ext}"
