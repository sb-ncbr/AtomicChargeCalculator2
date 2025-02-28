"""Module for IO operations."""

import hashlib
import os
import shutil

import aiofiles
from fastapi import UploadFile

from .base import IOBase


class IOLocal(IOBase):
    """Local IO operations."""

    tmp_workdir: str = os.path.join("/", "tmp", "acc2")

    def create_tmp_dir(self, name: str = "") -> str:
        path = os.path.join(IOLocal.tmp_workdir, name)
        os.makedirs(path, exist_ok=True)

        return path

    def remove_tmp_dir(self, dir_name: str) -> None:
        shutil.rmtree(os.path.join(IOLocal.tmp_workdir, dir_name))

    def cp(self, path_src: str, path_dst: str) -> str:
        return shutil.copy(path_src, path_dst)

    def listdir(self, directory: str = ".") -> list[str]:
        return os.listdir(directory)

    async def store_upload_file(self, file: UploadFile, directory: str) -> tuple[str, str]:
        tmp_path: str = os.path.join(directory, IOBase.get_unique_filename(file.filename))
        hasher = hashlib.sha256()
        chunk_size = 1024 * 1024  # 1 MB

        async with aiofiles.open(tmp_path, "wb") as out_file:
            while content := await file.read(chunk_size):
                await out_file.write(content)
                hasher.update(content)

        # add hash to file name
        file_hash = hasher.hexdigest()
        new_filename = os.path.join(directory, f"{file_hash}_{file.filename}")
        os.rename(tmp_path, new_filename)

        return new_filename, file_hash

    def path_exists(self, path: str) -> bool:
        return os.path.exists(path)
