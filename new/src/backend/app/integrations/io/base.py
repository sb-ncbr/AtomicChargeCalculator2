"""Base class for the file system interaction service."""

from abc import ABC, abstractmethod
import datetime
import os
import uuid

from fastapi import UploadFile


class IOBase(ABC):
    """Service for interaction with the file system."""

    @abstractmethod
    def mkdir(self, path: str) -> str:
        """Creates directory.

        Args:
            path (str): Path to the directory which will be created.

        Returns:
            str: Path to the created directory.
        """
        raise NotImplementedError()

    @abstractmethod
    def rmdir(self, path: str) -> None:
        """Removes directory.

        Args:
            path (str): Path to the directory which will be removed.
        """
        raise NotImplementedError()

    @abstractmethod
    def rm(self, path: str) -> None:
        """Removes file.

        Args:
            path (str): Path to the file which will be removed.
        """
        raise NotImplementedError()

    @abstractmethod
    def last_modified(self, path: str) -> datetime.datetime:
        """Returns the last modified time of a file.

        Args:
            path (str): Path to the file.

        Returns:
            datetime.datetime: Last modified utc timestamp.
        """
        raise NotImplementedError()

    @abstractmethod
    def dir_size(self, path: str) -> int:
        """Returns the size of a directory.

        Args:
            path (str): Path to the directory.

        Returns:
            int: Size of the directory in bytes.
        """
        raise NotImplementedError()

    @abstractmethod
    def file_size(self, path: str) -> int:
        """Returns the size of a file.

        Args:
            path (str): Path to the file.

        Returns:
            int: Size of the file in bytes.
        """
        raise NotImplementedError()

    @abstractmethod
    def cp(self, path_src: str, path_dst: str) -> str:
        """Copies file from 'path_src' to 'path_dst'.

        Args:
            path_src (str): Location of a file to copy.
            path_dst (str): Where to copy the file.

        Returns:
            str: Path to the copied file.
        """
        raise NotImplementedError()

    @abstractmethod
    def symlink(self, path_src: str, path_dst: str) -> None:
        """Creates a symlink from path_src to path_dst.

        Args:
            path_src (str): Location of a file to symlink.
            path_dst (str): Where to symlink the file.
        """
        raise NotImplementedError()

    @abstractmethod
    def zip(self, path: str, destination: str) -> str:
        """Zips the provided directory.

        Args:
            path (str): Path to directory to zip.
            destination (str): Where to store the zipped directory (without extension).

        Returns:
            str: Path to the zipped directory.
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
    async def write_file(self, path: str, content: str) -> None:
        """Writes content to a file.

        Args:
            path (str): Path to the file.
            content (str): Content to write to the file.
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
