import datetime
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Generator
import pytest

from app.integrations.io.io import IOLocal


@pytest.fixture
def io_service() -> Generator[tuple[IOLocal, Path], Any, None]:
    """Fixture for IO service."""

    test_dir = Path(tempfile.mkdtemp())
    io = IOLocal()

    yield io, test_dir

    shutil.rmtree(test_dir)


class TestIOService:
    def test_mkdir(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        new_dir = base_dir / "new_dir"

        # Act
        result = io.mkdir(str(new_dir))

        # Assert
        assert result == str(new_dir)
        assert new_dir.is_dir()
        assert new_dir.exists()

    def test_rmdir(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        new_dir = base_dir / "dir_to_remove"
        os.makedirs(str(new_dir))

        # Act
        io.rmdir(str(new_dir))

        # Assert
        assert not new_dir.exists()

    def test_rm(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        test_file = os.path.join(base_dir, "file_to_remove.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Act
        io.rm(test_file)

        # Assert
        assert not os.path.exists(test_file)

    def test_last_modified(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        test_file = os.path.join(base_dir, "test_modified.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Act
        now = datetime.datetime.now(datetime.timezone.utc)
        result = io.last_modified(test_file)

        # Assert
        assert abs((result - now).total_seconds()) < 5  # Within 5 seconds

    def test_dir_size(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        test_dir = os.path.join(base_dir, "test_size_dir")
        os.makedirs(test_dir)

        # Create some files with known sizes (100 bytes and 150 bytes)
        with open(os.path.join(test_dir, "file1.txt"), "w") as f:
            f.write("a" * 100)

        with open(os.path.join(test_dir, "file2.txt"), "w") as f:
            f.write("b" * 150)

        # Act
        result = io.dir_size(test_dir)

        assert result == 250  # 100 + 150 bytes

    def test_file_size(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        test_file = os.path.join(base_dir, "test_file_size.txt")

        # Create a file with known size (200 bytes)
        with open(test_file, "w") as f:
            f.write("a" * 200)

        # Act
        result = io.file_size(test_file)

        # Assert
        assert result == 200

    def test_cp(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        src_file = os.path.join(base_dir, "source.txt")
        dst_file = os.path.join(base_dir, "destination.txt")

        with open(src_file, "w") as f:
            f.write("test copy content")

        # Act
        result = io.cp(src_file, dst_file)

        # Assert
        assert result == dst_file
        assert os.path.exists(dst_file)

        # Also verify the content
        with open(dst_file, "r") as f:
            content = f.read()
        assert content == "test copy content"

    def test_symlink(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        src_file = os.path.join(base_dir, "symlink_source.txt")
        dst_link = os.path.join(base_dir, "symlink_dest.txt")

        with open(src_file, "w") as f:
            f.write("test symlink content")

        try:
            # Act
            io.symlink(src_file, dst_link)

            # Assert
            assert os.path.islink(dst_link)
            assert os.path.exists(dst_link)

            # Verify the content can be accessed through the symlink
            with open(dst_link, "r") as f:
                content = f.read()
            assert content == "test symlink content"
        except OSError:
            # Skipping on Windows
            pytest.skip("Symlinks not supported on this platform/environment")

    def test_zip(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        src_dir = os.path.join(base_dir, "dir_to_zip")
        os.makedirs(src_dir)

        # Create some files to zip
        with open(os.path.join(src_dir, "file1.txt"), "w") as f:
            f.write("test zip content 1")
        with open(os.path.join(src_dir, "file2.txt"), "w") as f:
            f.write("test zip content 2")

        # Act
        zip_dest = os.path.join(base_dir, "zipped_dir")
        result = io.zip(src_dir, zip_dest)

        # Assert
        assert result == f"{zip_dest}.zip"
        assert os.path.exists(result)

    def test_listdir(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service

        # Create some files and directories
        os.makedirs(os.path.join(base_dir, "subdir1"))
        os.makedirs(os.path.join(base_dir, "subdir2"))
        with open(os.path.join(base_dir, "file1.txt"), "w") as f:
            f.write("test content")

        # Act
        result = io.listdir(base_dir)

        # Assert
        assert set(result) == {"subdir1", "subdir2", "file1.txt"}

    @pytest.mark.asyncio
    async def test_write_file(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        test_file = os.path.join(base_dir, "test_write.txt")
        test_content = "test write content"

        # Act
        await io.write_file(test_file, test_content)

        # Assert
        assert os.path.exists(test_file)

        # Also verify the content
        with open(test_file, "r") as f:
            written_content = f.read()
        assert written_content == test_content

    def test_path_exists(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        test_file = os.path.join(base_dir, "test_exists.txt")

        # File doesn't exist yet
        assert not io.path_exists(test_file)

        with open(test_file, "w") as f:
            f.write("test content")

        # File now exists
        assert io.path_exists(test_file)

    def test_error_handling_nonexistent_path(self, io_service: tuple[IOLocal, Path]) -> None:
        # Arrange
        io, base_dir = io_service
        nonexistent_path = os.path.join(base_dir, "does_not_exist")

        # Act & Assert: These operations should raise exceptions
        with pytest.raises(FileNotFoundError):
            io.rm(nonexistent_path)

        with pytest.raises(FileNotFoundError):
            io.rmdir(nonexistent_path)
