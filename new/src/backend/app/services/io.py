"""Service for handling file operations."""

import json
import os
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv
from fastapi import UploadFile

from core.logging.base import LoggerBase
from core.integrations.io.base import IOBase
from core.models.calculation import ChargeCalculationConfigDto


load_dotenv()


class IOService:
    """Service for handling file operations."""

    workdir = Path(os.environ.get("ACC2_DATA_DIR"))
    examples_dir = Path(os.environ.get("ACC2_EXAMPLES_DIR"))

    def __init__(self, io: IOBase, logger: LoggerBase):
        self.io = io
        self.logger = logger

    def create_dir(self, path: str) -> None:
        """Create directory based on path."""

        self.logger.info(f"Creating directory {path}")

        try:
            self.io.mkdir(path)
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

    def zip_charges(self, directory: str) -> str:
        """Create archive from directory."""

        self.logger.info(f"Creating archive from {directory}.")

        try:
            archive_dir = Path(directory) / "archive"
            self.io.mkdir(str(archive_dir))

            for extension in ["cif", "pqr", "txt", "mol2"]:
                self.io.mkdir(str(archive_dir / extension))

            for file in self.io.listdir(directory):
                extension = file.rsplit(".", 1)[-1]
                file_path = str(Path(directory) / file)

                if extension in ["pqr", "txt", "mol2"]:
                    new_name = self.parse_filename(file)[-1]  # removing hash from filename
                    self.io.cp(file_path, str(Path(archive_dir) / extension / new_name))
                elif extension == "cif":
                    self.io.cp(file_path, str(Path(archive_dir) / extension))

            return self.io.zip(archive_dir, archive_dir)
        except Exception as e:
            self.logger.error(f"Error creating archive from {directory}: {e}")
            raise e

    def listdir(self, directory: str) -> list[str]:
        """List directory contents."""
        return self.io.listdir(directory)

    def path_exists(self, path: str) -> bool:
        """Check if path exists."""

        return self.io.path_exists(path)

    def get_file_storage_path(self, user_id: str | None = None) -> str:
        """Get path to file storage.

        Args:
            user_id (str | None, optional): Id of user. Defaults to None.

        Returns:
            str: Path to users file storage if user_id is provided.
                Path to guest file storage if user_id is None.
        """
        if user_id is not None:
            path = self.workdir / "user" / user_id / "files"
        else:
            path = self.workdir / "guest" / "files"

        return str(path)

    def get_computation_path(self, computation_id: str, user_id: str | None = None) -> str:
        """Get path to computation directory.

        Args:
            computation_id (str): Id of computation.
            user_id (str | None, optional): Id of user. Defaults to None.

        Returns:
            str: Returns path to computation directory of a given (users/guest) computation.
        """

        if user_id is not None:
            path = self.workdir / "user" / user_id / "computations" / computation_id
        else:
            path = self.workdir / "guest" / "computations" / computation_id

        return str(path)

    def get_inputs_path(self, computation_id: str, user_id: str | None = None) -> str:
        """Get path to inputs of a provided computation.

        Args:
            computation_id (str): Id of computation.
            user_id (str | None, optional): Id of user. Defaults to None.

        Returns:
            str: Returns path to input of a given (users/guest) computation.
        """

        if user_id is not None:
            path = self.workdir / "user" / user_id / "computations" / computation_id / "input"
        else:
            path = self.workdir / "guest" / "computations" / computation_id / "input"

        return str(path)

    def get_charges_path(self, computation_id: str, user_id: str | None = None) -> str:
        """Get path to charges directory of a provided computation.

        Args:
            computation_id (str): Id of the computation.
            file (str): Name of the file.
            user_id (str | None, optional): Id of the user. Defaults to None.

        Returns:
            str: Path to charges directory of a given (users/guest) computation.
        """

        if user_id is not None:
            path = self.workdir / "user" / user_id / "computations" / computation_id / "charges"
        else:
            path = self.workdir / "guest" / "computations" / computation_id / "charges"

        return str(path)

    def get_example_path(self, example_id: str) -> str:
        """Get path to example directory."""
        path = self.examples_dir / example_id
        return str(path)

    def prepare_inputs(
        self, user_id: str | None, computation_id: str, file_hashes: list[str]
    ) -> None:
        """Prepare input files for computation."""

        inputs_path = self.get_inputs_path(computation_id, user_id)
        files_path = self.get_file_storage_path(user_id)
        self.create_dir(inputs_path)
        self.create_dir(files_path)

        for file_hash in file_hashes:
            file_name = next(
                (
                    file
                    for file in self.listdir(files_path)
                    if self.parse_filename(file)[0] == file_hash
                ),
                None,
            )

            if not file_name:
                self.logger.warn(
                    f"File with hash {file_hash} not found in {inputs_path}, skipping."
                )
                continue

            src_path = str(Path(files_path) / file_name)
            dst_path = str(Path(inputs_path) / file_name)
            try:
                self.io.symlink(src_path, dst_path)
            except Exception as e:
                self.logger.warn(
                    f"Unable to create symlink from {src_path} to {dst_path}: {str(e)}"
                )

    async def store_configs(
        self,
        computation_id: str,
        configs: list[ChargeCalculationConfigDto],
        user_id: str | None = None,
    ) -> None:
        """Store configs for computation to a json file."""

        self.logger.info(f"Storing configs for computation. {computation_id}")

        try:
            path = Path(self.get_computation_path(computation_id, user_id))
            config_path = str(path / "configs.json")
            await self.io.write_file(
                config_path, json.dumps([config.model_dump() for config in configs], indent=4)
            )
        except Exception as e:
            self.logger.error(f"Unable to store configs: {e}")
            raise e

    def get_filepath(self, file_hash: str, user_id: str | None) -> str | None:
        """Get path to file with provided hash.

        Args:
            file_hash (str): File hash.
            user_id (str | None): User id.

        Returns:
            str: Path to file.
        """

        try:
            path = Path(self.get_file_storage_path(user_id))
            for file in self.listdir(str(path)):
                curr_hash, _ = self.parse_filename(file)
                if curr_hash == file_hash:
                    return str(path / file)

            return None
        except Exception as e:
            self.logger.error(f"Unable to get file path: {e}")
            raise e

    def parse_filename(self, filename: str) -> Tuple[str, str]:
        """Parse filename to get file hash and name.

        Args:
            filename (str): Filename in format <sha256_hash>_<file_name>.

        Raises:
            ValueError: If filename is not in the correct format.

        Returns:
            Tuple[str, str]: Tuple with file hash and name.
        """

        sha256_hash_length = 64
        parts = filename.split("_", 1)

        if (len(parts) != 2) or (len(parts[0]) != sha256_hash_length):
            self.logger.error(f"Invalid filename format: {filename}")
            raise ValueError("Invalid filename format.")

        file_hash, file_name = parts

        return file_hash, file_name
