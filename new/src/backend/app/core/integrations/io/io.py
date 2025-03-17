"""Module for IO operations."""

import hashlib
import os
import shutil

import aiofiles
from dotenv import load_dotenv
from fastapi import UploadFile

from .base import IOBase

load_dotenv()


class IOLocal(IOBase):
    """Local IO operations."""

    def mkdir(self, path: str) -> str:
        os.makedirs(path, exist_ok=True)
        return path

    def rmdir(self, path: str) -> None:
        shutil.rmtree(path)

    def cp(self, path_src: str, path_dst: str) -> str:
        return shutil.copy(path_src, path_dst)

    def zip(self, path: str, destination: str) -> str:
        return shutil.make_archive(destination, "zip", path)

    def listdir(self, directory: str = ".") -> list[str]:
        return os.listdir(directory)

    async def store_upload_file(self, file: UploadFile, directory: str) -> tuple[str, str]:
        tmp_path: str = os.path.join(directory, IOBase.get_unique_filename(file.filename))
        hasher = hashlib.sha256()
        chunk_size = 1024 * 1024  # 1 MB

        async with aiofiles.open(tmp_path, "wb") as out_file:
            while content := await file.read(chunk_size):
                unix_content = content.replace(b"\r", b"")
                await out_file.write(unix_content)
                hasher.update(unix_content)

        # add hash to file name
        file_hash = hasher.hexdigest()
        new_filename = os.path.join(directory, f"{file_hash}_{file.filename}")
        os.rename(tmp_path, new_filename)

        return new_filename, file_hash

    def path_exists(self, path: str) -> bool:
        return os.path.exists(path)
