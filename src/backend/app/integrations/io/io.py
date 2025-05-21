"""Module for IO operations."""

import datetime
import hashlib
import os
import pathlib
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

    def rm(self, path: str) -> None:
        os.remove(path)

    def cp(self, path_src: str, path_dst: str) -> str:
        return shutil.copy(path_src, path_dst)

    def symlink(self, path_src: str, path_dst: str) -> None:
        os.symlink(path_src, path_dst)

    def last_modified(self, path: str) -> datetime.datetime:
        ppath = pathlib.Path(path)
        if ppath.exists():
            timestamp = ppath.lstat().st_mtime
            return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)

        return 0.0

    def dir_size(self, path: str) -> int:
        # Also checking if path exsits since broken symlinks will throw an error
        return sum(p.lstat().st_size if p.exists() else 0 for p in pathlib.Path(path).rglob("*"))

    def file_size(self, path: str) -> int:
        # Also checking if path exsits since broken symlinks will throw an error
        ppath = pathlib.Path(path)
        return ppath.lstat().st_size if ppath.exists() else 0

    def zip(self, path: str, destination: str) -> str:
        return shutil.make_archive(destination, "zip", path)

    def listdir(self, directory: str = ".") -> list[str]:
        try:
            return os.listdir(directory)
        except FileNotFoundError:
            return []

    async def store_upload_file(self, file: UploadFile, directory: str) -> tuple[str, str]:
        tmp_path: str = os.path.join(directory, IOBase.get_unique_filename(file.filename or "file"))
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

    async def write_file(self, path: str, content: str) -> None:
        """Writes content to a file.

        Args:
            path (str): Path to the file.
            content (str): Content to write to the file.
        """

        async with aiofiles.open(path, "w") as out_file:
            await out_file.write(content)

    async def read_file(self, path: str) -> str:
        """Reads content from a file.

        Args:
            path (str): Path to the file.

        Returns:
            str: Content of the file.
        """

        async with aiofiles.open(path, "r") as in_file:
            return await in_file.read()

    def path_exists(self, path: str) -> bool:
        return os.path.exists(path)
