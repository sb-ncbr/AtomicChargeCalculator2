"""Service for handling file operations."""

import os


from dotenv import load_dotenv
from fastapi import UploadFile

from core.logging.base import LoggerBase
from core.integrations.io.base import IOBase


load_dotenv()


class IOService:
    """Service for handling file operations."""

    def __init__(self, io: IOBase, logger: LoggerBase):
        self.io = io
        self.logger = logger

    def create_tmp_dir(self, name: str) -> str:
        """Create temporary directory with the provided name."""

        if name == "":
            raise ValueError("Name cannot be empty.")

        try:
            self.logger.info(f"Creating temporary directory with name: {name}")
            path = self.io.create_tmp_dir(name)
            return path
        except Exception as e:
            self.logger.info(f"Unable to create temporary directory '{name}': {e}")
            raise e

    def remove_tmp_dir(self, path: str) -> None:
        """Remove temporary directory."""

        self.logger.info(f"Removing temporary directory {path}")

        try:
            self.io.remove_tmp_dir(path)
        except Exception as e:
            self.logger.error(f"Unable to remove temporary directory '{path}': {e}")
            raise e

    def create_dir(self, path: str) -> None:
        """Create directory."""

        self.logger.info(f"Creating directory {path}")

        try:
            self.io.create_dir(path)
        except Exception as e:
            self.logger.error(f"Unable to create directory '{path}': {e}")
            raise e

    def cp(self, path_from: str, path_to: str) -> str:
        """Copy file from source to destination."""

        self.logger.info(f"Copying from {path_from} to {path_to}.")

        try:
            path = self.io.cp(path_from, path_to)
            return path
        except Exception as e:
            self.logger.error(f"Unable to copy '{path_from}' to '{path_to}': {e}")
            raise e

    async def store_upload_file(self, file: UploadFile, directory: str) -> tuple[str, str]:
        """Store uploaded file in the provided directory."""
        self.logger.info(f"Storing file {file.filename}.")

        try:
            return await self.io.store_upload_file(file, directory)
        except Exception as e:
            self.logger.error(f"Error storing file {file.filename}: {e}")
            raise e

    def listdir(self, directory: str) -> list[str]:
        """List directory contents."""
        return self.io.listdir(directory)

    def path_exists(self, path: str) -> bool:
        """Check if path exists."""
        return self.io.path_exists(path)

    def get_input_path(self, computation_id: str) -> str:
        """Get path to input directory."""
        return os.path.join(self.io.tmp_workdir, computation_id, "input")

    def get_charges_path(self, computation_id: str) -> str:
        """Get path to charges directory."""
        return os.path.join(self.io.tmp_workdir, computation_id, "charges")

    def get_example_path(self, example_id: str) -> str:
        """Get path to example directory."""
        return os.path.join(os.environ.get("ACC2_EXAMPLES_DIR"), example_id)
