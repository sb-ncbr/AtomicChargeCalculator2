import os

import aiofiles
from fastapi import UploadFile

from core.logging.base import LoggerBase
from core.integrations.io.base import IOBase


class IOService:
    workdir: str = os.path.join("/", "tmp", "acc2")

    def __init__(self, io: IOBase, logger: LoggerBase):
        self.io = io
        self.logger = logger

    def create_tmp_dir(self, name: str = "") -> str:
        self.logger.info(f"Creating temporary directory with name: {name or '<empty>'}")

        path = self.io.create_tmp_dir(name)

        self.logger.info(f"Created temporary directory: {path}")

        return path

    def remove_tmp_dir(self, path: str) -> None:
        self.logger.info(f"Clearing temporary directory {path}")
        self.remove_tmp_dir(path)

    def cp(self, path_from: str, path_to: str) -> str:
        self.logger.info(f"Copying from {path_from} to {path_to}.")

        path = self.io.cp(path_from, path_to)

        self.logger.info(f"Successfully copied from {path_from} to {path_to}.")

        return path

    async def store_upload_file(self, file: UploadFile, dir: str) -> str | None:
        os.makedirs(dir, exist_ok=True)
        path: str = os.path.join(dir, IOService.get_unique_filename(file.filename))
        chunk_size = 64 * 1024  # 64 KB
        try:
            async with aiofiles.open(path, "wb") as out_file:
                while content := await file.read(chunk_size):
                    await out_file.write(content)

            self.logger.info(f"Successfully stored file {file.filename}.")
            return path
        except Exception as e:
            self.logger.error(f"Error storing file {file.filename}: {e}")
            return None

    @staticmethod
    def get_unique_filename(filename: str) -> str:
        import uuid

        base, ext = os.path.splitext(filename)
        return f"{str(uuid.uuid4())}_{base}{ext}"
