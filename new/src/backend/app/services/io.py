"""Service for handling file operations."""

import aiofiles
import hashlib
import os
import uuid

from fastapi import UploadFile

from core.logging.base import LoggerBase
from core.integrations.io.base import IOBase


class IOService:
    """Service for handling file operations."""

    workdir: str = os.path.join("/", "tmp", "acc2")

    def __init__(self, io: IOBase, logger: LoggerBase):
        self.io = io
        self.logger = logger

    def create_tmp_dir(self, name: str) -> str:
        """Create temporary directory with the provided name."""

        if name == "":
            raise ValueError("Name cannot be empty.")

        self.logger.info(f"Creating temporary directory with name: {name}")

        path = self.io.create_tmp_dir(name)

        self.logger.info(f"Created temporary directory: {path}")

        return path

    def remove_tmp_dir(self, path: str) -> None:
        """Remove temporary directory."""

        self.logger.info(f"Clearing temporary directory {path}")
        self.io.remove_tmp_dir(path)

    def cp(self, path_from: str, path_to: str) -> str:
        """Copy file from source to destination."""

        self.logger.info(f"Copying from {path_from} to {path_to}.")

        path = self.io.cp(path_from, path_to)

        self.logger.info(f"Successfully copied from {path_from} to {path_to}.")

        return path

    async def store_upload_file(self, file: UploadFile, dir_name: str) -> tuple[str, str]:
        """Store uploaded file in the provided directory."""

        os.makedirs(dir_name, exist_ok=True)
        path: str = os.path.join(dir_name, IOService.get_unique_filename(file.filename))
        hasher = hashlib.sha256()
        chunk_size = 64 * 1024  # 64 KB

        try:
            self.logger.info(f"Storing file {file.filename}.")
            async with aiofiles.open(path, "wb") as out_file:
                while content := await file.read(chunk_size):
                    await out_file.write(content)
                    hasher.update(content)

            return path, hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"Error storing file {file.filename}: {e}")
            raise e

    @staticmethod
    def get_unique_filename(filename: str) -> str:
        """Generate unique filename."""

        base, ext = os.path.splitext(filename)
        return f"{str(uuid.uuid4())}_{base}{ext}"
