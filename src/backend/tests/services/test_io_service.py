import datetime
import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
import pytest

from app.models.calculation import CalculationConfigDto
from app.services.io import IOService


@pytest.fixture
def async_io_mock():
    return AsyncMock()


@pytest.fixture
def io_mock():
    return Mock()


@pytest.fixture
def logger_mock():
    return Mock()


@pytest.fixture
def io_service(io_mock, logger_mock):
    return IOService(io_mock, logger_mock)


@pytest.fixture
def async_io_service(async_io_mock, logger_mock):
    return IOService(async_io_mock, logger_mock)


@pytest.fixture
def test_data():
    return {
        "user_id": "test-user-id",
        "computation_id": "test-computation-id",
        "file_hash": "a" * 64,  # sha256
        "filename": f"{'' * 64}_test-file-name",
    }


class TestIOService:
    def test_create_dir(self, io_service, io_mock, logger_mock):
        """Test creating a directory."""
        test_path = "/path/to/test/dir"

        io_service.create_dir(test_path)

        io_mock.mkdir.assert_called_once_with(test_path)
        logger_mock.info.assert_called_once()

    def test_create_dir_exception(self, io_service, io_mock, logger_mock):
        """Test handling exceptions when creating a directory."""
        test_path = "/path/to/test/dir"

        io_mock.mkdir.side_effect = Exception("Directory creation failed")

        with pytest.raises(Exception):
            io_service.create_dir(test_path)

        logger_mock.error.assert_called_once()

    def test_cp(self, io_service, io_mock, logger_mock):
        """Test copying a file."""
        path_from = "/source/path"
        path_to = "/destination/path"
        expected_path = "/destination/path/file.txt"

        io_mock.cp.return_value = expected_path

        result = io_service.cp(path_from, path_to)

        io_mock.cp.assert_called_once_with(path_from, path_to)
        assert result == expected_path
        logger_mock.info.assert_called_once()

    def test_cp_exception(self, io_service, io_mock, logger_mock):
        """Test handling exceptions when copying a file."""
        path_from = "/source/path"
        path_to = "/destination/path"

        io_mock.cp.side_effect = Exception("File copy failed")

        with pytest.raises(Exception):
            io_service.cp(path_from, path_to)

        logger_mock.error.assert_called_once()

    def test_remove_file(self, io_service, io_mock, logger_mock, test_data):
        """Test removing a file."""
        filepath = f"/test/path/{test_data['filename']}"
        with patch.object(io_service, "get_filepath", return_value=filepath):
            io_service.remove_file(test_data["file_hash"], test_data["user_id"])

            io_mock.rm.assert_called_once_with(filepath)
            logger_mock.info.assert_called_once()

    def test_remove_file_not_found(self, io_service, io_mock, test_data):
        """Test handling when file to remove is not found."""
        with patch.object(io_service, "get_filepath", return_value=None):
            io_service.remove_file(test_data["file_hash"], test_data["user_id"])

            io_mock.rm.assert_not_called()

    def test_remove_file_exception(self, io_service, io_mock, logger_mock, test_data):
        """Test handling exceptions when removing a file."""
        filepath = f"/test/path/{test_data['filename']}"
        with patch.object(io_service, "get_filepath", return_value=filepath):
            io_mock.rm.side_effect = Exception("Failed to remove file")

            with pytest.raises(Exception):
                io_service.remove_file(test_data["file_hash"], test_data["user_id"])

            logger_mock.error.assert_called_once()

    def test_zip_charges(self, io_service, io_mock):
        """Test creating an archive from directory."""
        directory = "/test/directory"
        archive_path = "/test/directory/archive"
        expected_result = f"{archive_path}.zip"

        io_mock.listdir.return_value = [
            "hash1_file1.pqr",
            "hash1_file2.txt",
            "hash1_file3.mol2",
            "hash1_file4.cif",
        ]
        io_mock.zip.return_value = expected_result

        with patch.object(io_service, "parse_filename", return_value=("hash", "filename")):
            result = io_service.zip_charges(directory)

            assert io_mock.mkdir.call_count == 5  # archive dir + 4 extension dirs

            assert io_mock.cp.call_count == len(io_mock.listdir.return_value)

            io_mock.zip.assert_called_once_with(archive_path, archive_path)
            assert result == expected_result

    def test_zip_charges_exception(self, io_service, io_mock, logger_mock):
        """Test handling exceptions when creating an archive."""
        directory = "/test/directory"

        io_mock.mkdir.side_effect = Exception("Failed to create directory")

        with pytest.raises(Exception):
            io_service.zip_charges(directory)

        logger_mock.error.assert_called_once()

    def test_listdir(self, io_service, io_mock):
        """Test listing directory contents."""
        directory = "/test/directory"
        expected_files = ["file1.txt", "file2.txt"]

        io_mock.listdir.return_value = expected_files

        result = io_service.listdir(directory)

        io_mock.listdir.assert_called_once_with(directory)
        assert result == expected_files

    def test_path_exists(self, io_service, io_mock):
        """Test checking if path exists."""
        path = "/test/path"

        # path exists
        io_mock.path_exists.return_value = True
        result = io_service.path_exists(path)

        io_mock.path_exists.assert_called_once_with(path)
        assert result is True

        # path doesn't exist
        io_mock.path_exists.reset_mock()
        io_mock.path_exists.return_value = False
        result = io_service.path_exists(path)

        io_mock.path_exists.assert_called_once_with(path)
        assert result is False

    def test_get_storage_path(self, io_service):
        """Test getting storage path."""
        # logged in user
        user_id = "test_user"
        result = io_service.get_storage_path(user_id)
        expected = str(io_service.workdir / "user" / user_id)
        assert result == expected

        # guest user
        result = io_service.get_storage_path(None)
        expected = str(io_service.workdir / "guest")
        assert result == expected

    def test_get_file_storage_path(self, io_service):
        """Test getting file storage path."""
        # logged in user
        user_id = "test_user"
        result = io_service.get_file_storage_path(user_id)
        expected = str(io_service.workdir / "user" / user_id / "files")
        assert result == expected

        # guest user
        result = io_service.get_file_storage_path(None)
        expected = str(io_service.workdir / "guest" / "files")
        assert result == expected

    def test_get_computations_path(self, io_service):
        """Test getting computations path."""
        # logged in user
        user_id = "test_user"
        result = io_service.get_computations_path(user_id)
        expected = str(io_service.workdir / "user" / user_id / "computations")
        assert result == expected

        # guest user
        result = io_service.get_computations_path(None)
        expected = str(io_service.workdir / "guest" / "computations")
        assert result == expected

    def test_get_computation_path(self, io_service):
        """Test getting computation path."""
        computation_id = "test_comp"

        # logged in user
        user_id = "test_user"
        result = io_service.get_computation_path(computation_id, user_id)
        expected = str(io_service.workdir / "user" / user_id / "computations" / computation_id)
        assert result == expected

        # guest user
        result = io_service.get_computation_path(computation_id, None)
        expected = str(io_service.workdir / "guest" / "computations" / computation_id)
        assert result == expected

    def test_get_inputs_path(self, io_service):
        """Test getting inputs path."""
        computation_id = "test_comp"

        # logged in user
        user_id = "test_user"
        result = io_service.get_inputs_path(computation_id, user_id)
        expected = str(
            io_service.workdir / "user" / user_id / "computations" / computation_id / "input"
        )
        assert result == expected

        # guest user
        result = io_service.get_inputs_path(computation_id, None)
        expected = str(io_service.workdir / "guest" / "computations" / computation_id / "input")
        assert result == expected

    def test_get_charges_path(self, io_service):
        """Test getting charges path."""
        computation_id = "test_comp"

        # logged in user
        user_id = "test_user"
        result = io_service.get_charges_path(computation_id, user_id)
        expected = str(
            io_service.workdir / "user" / user_id / "computations" / computation_id / "charges"
        )
        assert result == expected

        # guest user
        result = io_service.get_charges_path(computation_id, None)
        expected = str(io_service.workdir / "guest" / "computations" / computation_id / "charges")
        assert result == expected

    def test_get_example_path(self, io_service):
        """Test getting example path."""
        example_id = "test_example"

        result = io_service.get_example_path(example_id)
        expected = str(io_service.examples_dir / example_id)

        assert result == expected

    def test_prepare_inputs(self, io_service, io_mock, test_data):
        """Test preparing input files for computation."""
        computation_id = test_data["computation_id"]
        user_id = test_data["user_id"]
        file_hashes = [test_data["file_hash"]]

        inputs_path = "/test/inputs/path"
        files_path = "/test/files/path"
        with (
            patch.object(io_service, "get_inputs_path", return_value=inputs_path),
            patch.object(io_service, "get_file_storage_path", return_value=files_path),
        ):
            io_mock.listdir.return_value = [test_data["filename"]]
            with patch.object(
                io_service, "parse_filename", return_value=(test_data["file_hash"], "test_file.txt")
            ):
                io_service.prepare_inputs(user_id, computation_id, file_hashes)

                assert io_mock.mkdir.call_count == 2

                src_path = str(Path(files_path) / test_data["filename"])
                dst_path = str(Path(inputs_path) / test_data["filename"])
                io_mock.symlink.assert_called_once_with(src_path, dst_path)

    def test_prepare_inputs_file_not_found(self, io_service, io_mock, logger_mock, test_data):
        """Test preparing inputs when file is not found."""
        computation_id = test_data["computation_id"]
        user_id = test_data["user_id"]
        file_hashes = [test_data["file_hash"]]

        inputs_path = "/test/inputs/path"
        files_path = "/test/files/path"
        with (
            patch.object(io_service, "get_inputs_path", return_value=inputs_path),
            patch.object(io_service, "get_file_storage_path", return_value=files_path),
        ):
            io_mock.listdir.return_value = []

            io_service.prepare_inputs(user_id, computation_id, file_hashes)

            logger_mock.warn.assert_called_once()
            io_mock.symlink.assert_not_called()

    @pytest.mark.asyncio
    async def test_store_configs(self, async_io_service, async_io_mock, test_data):
        """Test storing configs for computation."""
        computation_id = test_data["computation_id"]
        user_id = test_data["user_id"]
        configs = [
            CalculationConfigDto(method="method1", parameters="param1"),
            CalculationConfigDto(method="method2", parameters="param2"),
            CalculationConfigDto(method="method2", parameters=None),
        ]

        comp_path = "/test/computation/path"
        with patch.object(async_io_service, "get_computation_path", return_value=comp_path):
            await async_io_service.store_configs(computation_id, configs, user_id)

            config_path = str(Path(comp_path) / "configs.json")
            expected_content = json.dumps([config.model_dump() for config in configs], indent=4)
            async_io_mock.write_file.assert_called_once_with(config_path, expected_content)

    @pytest.mark.asyncio
    async def test_store_configs_exception(
        self, async_io_service, async_io_mock, logger_mock, test_data
    ):
        """Test handling exceptions when storing configs."""
        computation_id = test_data["computation_id"]
        user_id = test_data["user_id"]
        configs = [CalculationConfigDto(method="method1", parameters="param1")]

        comp_path = "/test/computation/path"
        with patch.object(async_io_service, "get_computation_path", return_value=comp_path):
            async_io_mock.write_file.side_effect = Exception("Failed to write file")

            with pytest.raises(Exception):
                await async_io_service.store_configs(computation_id, configs, user_id)

            logger_mock.error.assert_called_once()

    def test_get_filepath(self, io_service, io_mock, test_data):
        """Test getting filepath for a file hash."""
        file_hash = test_data["file_hash"]
        user_id = test_data["user_id"]
        filename = test_data["filename"]

        storage_path = "/test/files/path"
        with patch.object(io_service, "get_file_storage_path", return_value=storage_path):
            io_mock.listdir.return_value = [filename]

            with patch.object(
                io_service, "parse_filename", return_value=(file_hash, "test_file.txt")
            ):
                result = io_service.get_filepath(file_hash, user_id)

                expected_path = str(Path(storage_path) / filename)
                assert result == expected_path

    def test_get_filepath_not_found(self, io_service, io_mock, logger_mock, test_data):
        """Test getting filepath when file hash is not found."""
        file_hash = test_data["file_hash"]
        user_id = test_data["user_id"]

        storage_path = "/test/files/path"
        with patch.object(io_service, "get_file_storage_path", return_value=storage_path):
            io_mock.listdir.return_value = ["other_hash_file.txt"]

            with patch.object(
                io_service, "parse_filename", return_value=("other_hash", "file.txt")
            ):
                result = io_service.get_filepath(file_hash, user_id)

                assert result is None

    def test_get_filepath_exception(self, io_service, io_mock, logger_mock, test_data):
        """Test handling exceptions when getting filepath."""
        file_hash = test_data["file_hash"]
        user_id = test_data["user_id"]

        storage_path = "/test/files/path"
        with patch.object(io_service, "get_file_storage_path", return_value=storage_path):
            io_mock.listdir.side_effect = Exception("Failed to list directory")

            with pytest.raises(Exception):
                io_service.get_filepath(file_hash, user_id)

            logger_mock.error.assert_called_once()

    def test_get_last_modification(self, io_service, io_mock, test_data):
        """Test getting last modification time."""
        file_hash = test_data["file_hash"]
        user_id = test_data["user_id"]
        file_path = f"/test/path/{test_data['filename']}"
        expected_time = datetime.datetime.now()

        with patch.object(io_service, "get_filepath", return_value=file_path):
            io_mock.last_modified.return_value = expected_time

            result = io_service.get_last_modification(file_hash, user_id)

            io_mock.last_modified.assert_called_once_with(file_path)
            assert result == expected_time

    def test_get_last_modification_exception(self, io_service, io_mock, logger_mock, test_data):
        """Test handling exceptions when getting last modification time."""
        file_hash = test_data["file_hash"]
        user_id = test_data["user_id"]
        file_path = f"/test/path/{test_data['filename']}"

        with patch.object(io_service, "get_filepath", return_value=file_path):
            io_mock.last_modified.side_effect = Exception("Failed to get last modification time")

            with pytest.raises(Exception):
                io_service.get_last_modification(file_hash, user_id)

            logger_mock.error.assert_called_once()

    def test_get_file_size(self, io_service, io_mock, test_data):
        """Test getting file size."""
        file_hash = test_data["file_hash"]
        user_id = test_data["user_id"]
        file_path = f"/test/path/{test_data['filename']}"
        expected_size = 1024

        with patch.object(io_service, "get_filepath", return_value=file_path):
            io_mock.file_size.return_value = expected_size

            result = io_service.get_file_size(file_hash, user_id)

            io_mock.file_size.assert_called_once_with(file_path)
            assert result == expected_size

    def test_get_file_size_exception(self, io_service, io_mock, logger_mock, test_data):
        """Test handling exceptions when getting file size."""
        file_hash = test_data["file_hash"]
        user_id = test_data["user_id"]
        file_path = f"/test/path/{test_data['filename']}"

        with patch.object(io_service, "get_filepath", return_value=file_path):
            io_mock.file_size.side_effect = Exception("Failed to get file size")

            with pytest.raises(Exception):
                io_service.get_file_size(file_hash, user_id)

            logger_mock.error.assert_called_once()

    def test_free_guest_file_space_no_need(self, io_service, io_mock, logger_mock):
        """Test freeing guest file space when there's enough space."""
        path = "/test/guest/files"
        amount_to_free = 1000

        with patch.object(io_service, "get_file_storage_path", return_value=path):
            # sufficient space
            io_mock.dir_size.return_value = 1000  # currently using 1000 bytes
            io_service.guest_file_quota = 10000

            io_service.free_guest_file_space(amount_to_free)

            io_mock.rm.assert_not_called()
            logger_mock.info.assert_called_with(
                "Guest file space is sufficient. No need to free space."
            )

    def test_free_guest_file_space_success(self, io_service, io_mock, logger_mock):
        """Test successfully freeing guest file space."""
        path = "/test/guest/files"
        amount_to_free = 1000

        with patch.object(io_service, "get_file_storage_path", return_value=path):
            # insufficient space
            io_mock.dir_size.return_value = 2000  # currently using 2000 bytes
            io_service.guest_file_quota = 2500

            files = ["file1.txt", "file2.txt"]
            io_mock.listdir.return_value = files
            io_mock.last_modified.side_effect = [
                datetime.datetime(2023, 1, 1),  # file1 is older
                datetime.datetime(2023, 1, 2),  # file2 is newer
            ]
            io_mock.file_size.return_value = 1000  # each file is 1000 bytes

            io_service.free_guest_file_space(amount_to_free)

            # oldest file was deleted
            io_mock.rm.assert_called_once_with(str(Path(path) / "file1.txt"))

    def test_free_guest_file_space_not_enough_space(self, io_service, io_mock, logger_mock):
        """Test freeing guest file space when there's not enough space to free."""
        path = "/test/guest/files"
        amount_to_free = 3000

        with patch.object(io_service, "get_file_storage_path", return_value=path):
            # insufficient space
            io_mock.dir_size.return_value = 2000  # currently using 2000 bytes
            io_service.guest_file_quota = 1000  # quota is smaller than used space

            with pytest.raises(ValueError, match="Not enough space to free."):
                io_service.free_guest_file_space(amount_to_free)

    def test_free_guest_compute_space_no_need(self, io_service, io_mock, logger_mock):
        """Test freeing guest compute space when there's enough space."""
        path = "/test/guest/computations"

        with patch.object(io_service, "get_computations_path", return_value=path):
            # insufficient space
            io_mock.dir_size.return_value = 1000  # currently using 1000 bytes
            io_service.guest_compute_quota = 2000

            io_service.free_guest_compute_space()

            # Check no computations were deleted
            io_mock.rmdir.assert_not_called()
            logger_mock.info.assert_called_with(
                "Guest compute space is sufficient. No need to free space."
            )

    def test_free_guest_compute_space_success(self, io_service, io_mock, logger_mock):
        """Test successfully freeing guest compute space."""
        path = "/test/guest/computations"

        with patch.object(io_service, "get_computations_path", return_value=path):
            # insufficient space
            io_mock.dir_size.return_value = 3000  # currently using 3000 bytes
            io_service.guest_compute_quota = 2000

            computations = ["comp1", "comp2"]
            io_mock.listdir.return_value = computations
            io_mock.last_modified.side_effect = [
                datetime.datetime(2023, 1, 1),  # comp1 is older
                datetime.datetime(2023, 1, 2),  # comp2 is newer
            ]
            io_mock.dir_size.side_effect = [3000, 1500]

            io_service.free_guest_compute_space()

            # oldest computation was deleted
            io_mock.rmdir.assert_called_once_with(str(Path(path) / "comp1"))

    def test_delete_computation(self, io_service, io_mock, test_data):
        """Test deleting a computation."""
        computation_id = test_data["computation_id"]
        user_id = test_data["user_id"]

        comp_path = "/test/computation/path"
        with patch.object(io_service, "get_computation_path", return_value=comp_path):
            io_service.delete_computation(computation_id, user_id)

            io_mock.rmdir.assert_called_once_with(comp_path)

    def test_delete_computation_exception(self, io_service, io_mock, logger_mock, test_data):
        """Test handling exceptions when deleting a computation."""
        computation_id = test_data["computation_id"]
        user_id = test_data["user_id"]

        comp_path = "/test/computation/path"
        with patch.object(io_service, "get_computation_path", return_value=comp_path):
            io_mock.rmdir.side_effect = Exception("Failed to remove directory")

            with pytest.raises(Exception):
                io_service.delete_computation(computation_id, user_id)

                assert logger_mock.method_calls

    def test_parse_filename_valid(self, io_service):
        """Test parsing valid filename."""
        file_hash = "a" * 64
        file_name = "test_file.txt"
        filename = f"{file_hash}_{file_name}"

        result_hash, result_name = io_service.parse_filename(filename)

        assert result_hash == file_hash
        assert result_name == file_name

    def test_parse_filename_invalid_format(self, io_service, logger_mock):
        """Test parsing invalid filename format."""
        filename = "invalid-format-no-hash.txt"  # no underscore

        with pytest.raises(ValueError, match="Invalid filename format"):
            io_service.parse_filename(filename)

        logger_mock.error.assert_called_once()

    def test_parse_filename_invalid_hash_length(self, io_service, logger_mock):
        """Test parsing filename with invalid hash length."""
        file_hash = "a" * 10  # Only 10 chars instead of 64
        filename = f"{file_hash}_test_file.txt"

        with pytest.raises(ValueError, match="Invalid filename format"):
            io_service.parse_filename(filename)

        logger_mock.error.assert_called_once()

    def test_get_quota_user(self, io_service, io_mock):
        """Test getting quota for a user."""
        user_id = "test_user"
        storage_path = "/test/user/path"
        used_space = 1000
        quota = 5000

        with patch.object(io_service, "get_storage_path", return_value=storage_path):
            io_mock.dir_size.return_value = used_space
            io_service.user_quota = quota

            result_used, result_available, result_quota = io_service.get_quota(user_id)

            assert result_used == used_space
            assert result_available == quota - used_space
            assert result_quota == quota

    def test_get_quota_guest(self, io_service, io_mock):
        """Test getting quota for a guest."""
        storage_path = "/test/guest/path"
        used_space = 1000
        file_quota = 2000
        compute_quota = 3000

        with patch.object(io_service, "get_storage_path", return_value=storage_path):
            io_mock.dir_size.return_value = used_space
            io_service.guest_file_quota = file_quota
            io_service.guest_compute_quota = compute_quota

            result_used, result_available, result_quota = io_service.get_quota(None)

            assert result_used == used_space
            assert result_available == (file_quota + compute_quota) - used_space
            assert result_quota == file_quota + compute_quota

    def test_environment_variables(self, io_service):
        """Test that environment variables are properly loaded."""
        assert isinstance(io_service.workdir, Path)

        assert isinstance(io_service.examples_dir, Path)

        assert isinstance(io_service.user_quota, int)
        assert isinstance(io_service.guest_file_quota, int)
        assert isinstance(io_service.guest_compute_quota, int)

        assert isinstance(io_service.max_file_size, int)
        assert isinstance(io_service.max_upload_size, int)
