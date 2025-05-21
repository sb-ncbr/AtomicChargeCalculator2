import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from models.calculation import (
    CalculationConfigDto,
    CalculationDto,
    CalculationResultDto,
    CalculationSetPreviewDto,
)
from models.paging import PagedList
from models.molecule_info import MoleculeSetStats
from models.setup import AdvancedSettingsDto
from db.schemas.user import User  # noqa: F401
from db.schemas.calculation import (
    AdvancedSettings,
    Calculation,
    CalculationConfig,
    CalculationSet,
    CalculationSetStats,
)
from db.schemas.stats import (
    AtomTypeCount as AtomTypeCountModel,
    MoleculeSetStats as MoleculeSetStatsModel,
)
from db.repositories.calculation_set_repository import CalculationSetFilters
from services.calculation_storage import CalculationStorageService


@pytest.fixture
def logger_mock():
    return Mock()


@pytest.fixture
def set_repository_mock():
    return Mock()


@pytest.fixture
def calculation_repository_mock():
    return Mock()


@pytest.fixture
def config_repository_mock():
    return Mock()


@pytest.fixture
def stats_repository_mock():
    return Mock()


@pytest.fixture
def advanced_settings_repository_mock():
    return Mock()


@pytest.fixture
def session_manager_mock():
    session = MagicMock()

    context_manager = MagicMock()
    context_manager.__enter__.return_value = session

    session_manager = Mock()
    session_manager.session.return_value = context_manager
    return session_manager


@pytest.fixture
def service(
    logger_mock,
    set_repository_mock,
    calculation_repository_mock,
    config_repository_mock,
    stats_repository_mock,
    advanced_settings_repository_mock,
    session_manager_mock,
):
    return CalculationStorageService(
        logger=logger_mock,
        set_repository=set_repository_mock,
        calculation_repository=calculation_repository_mock,
        config_repository=config_repository_mock,
        stats_repository=stats_repository_mock,
        advanced_settings_repository=advanced_settings_repository_mock,
        session_manager=session_manager_mock,
    )


@pytest.fixture
def sample_molecule_set_stats():
    return MoleculeSetStatsModel(
        file_hash="hash123",
        total_molecules=10,
        total_atoms=100,
        atom_type_counts=[
            AtomTypeCountModel(symbol="C", count=50),
            AtomTypeCountModel(symbol="H", count=30),
            AtomTypeCountModel(symbol="O", count=20),
        ],
    )


@pytest.fixture
def sample_advanced_settings():
    return AdvancedSettingsDto(
        read_hetatm=True,
        ignore_water=False,
        permissive_types=True,
    )


@pytest.fixture
def sample_advanced_settings_entity():
    return AdvancedSettings(
        read_hetatm=True,
        ignore_water=False,
        permissive_types=True,
    )


@pytest.fixture
def sample_calculation_config():
    return CalculationConfigDto(method="method1", parameters="params1")


@pytest.fixture
def sample_calculation_config_entity():
    return CalculationConfig(method="method1", parameters="params1")


@pytest.fixture
def sample_calculation_result(sample_calculation_config):
    return CalculationResultDto(
        config=sample_calculation_config,
        calculations=[
            CalculationDto(
                file="file1.mol",
                file_hash="hash123",
                charges={},
                config=sample_calculation_config,
            )
        ],
    )


@pytest.fixture
def sample_calculation_set(sample_advanced_settings_entity, sample_calculation_config_entity):
    calculation_set = CalculationSet(
        id="d55a7af3-d1ee-4884-bce0-805efd5e1e64",
        user_id="user123",
        created_at=datetime.now(),
        advanced_settings=sample_advanced_settings_entity,
        configs=[sample_calculation_config_entity],
        molecule_set_stats_associations=[
            CalculationSetStats(molecule_set_id="hash123", file_name="file1.mol")
        ],
    )

    return calculation_set


class TestCalculationStorageService:
    def test_get_info(
        self,
        service,
        session_manager_mock,
        stats_repository_mock,
        sample_molecule_set_stats,
    ):
        """Test get_info method returns a value."""

        session = session_manager_mock.session().__enter__()
        stats_repository_mock.get.return_value = sample_molecule_set_stats

        result = service.get_info(session, "hash123")

        stats_repository_mock.get.assert_called_once_with(session, "hash123")
        assert result is not None
        assert result.total_molecules == 10
        assert result.total_atoms == 100
        assert len(result.atom_type_counts) == 3
        assert result.atom_type_counts[0].symbol == "C"
        assert result.atom_type_counts[0].count == 50

    def test_get_info_none(self, service, session_manager_mock, stats_repository_mock):
        """Test get_info method returns None when no value is found."""

        session = session_manager_mock.session().__enter__()
        stats_repository_mock.get.return_value = None

        result = service.get_info(session, "nonexistent")

        stats_repository_mock.get.assert_called_once_with(session, "nonexistent")
        assert result is None

    def test_get_calculations(
        self,
        service,
        session_manager_mock,
        set_repository_mock,
        sample_calculation_set,
        stats_repository_mock,
    ):
        """Test get_calculations method returns a PagedList of CalculationSetPreviewDtos."""

        set_repository_mock.get_all.return_value = PagedList(items=[sample_calculation_set])

        molecule_set_stats = MoleculeSetStats(
            {
                "total_molecules": 10,
                "total_atoms": 100,
                "atom_type_counts": [
                    {"symbol": "C", "count": 50},
                    {"symbol": "H", "count": 30},
                    {"symbol": "O", "count": 20},
                ],
            }
        )

        with patch.object(service, "get_info", return_value=molecule_set_stats):
            filters = CalculationSetFilters(
                page=1, page_size=10, order_by="created_at", order="desc"
            )
            result = service.get_calculations(filters)

            set_repository_mock.get_all.assert_called_once_with(
                session_manager_mock.session().__enter__(), filters
            )
            assert isinstance(result, PagedList)
            assert len(result.items) == 1
            assert isinstance(result.items[0], CalculationSetPreviewDto)
            assert str(result.items[0].id) == "d55a7af3-d1ee-4884-bce0-805efd5e1e64"
            assert len(result.items[0].files) == 1
            assert "file1.mol" in result.items[0].files

    def test_get_calculation_set(
        self,
        service,
        session_manager_mock,
        set_repository_mock,
        sample_calculation_set,
    ):
        """Test get_calculation_set method returns a calculation set."""

        set_repository_mock.get.return_value = sample_calculation_set

        result = service.get_calculation_set("d55a7af3-d1ee-4884-bce0-805efd5e1e64")

        set_repository_mock.get.assert_called_once_with(
            session_manager_mock.session().__enter__(), "d55a7af3-d1ee-4884-bce0-805efd5e1e64"
        )
        assert result == sample_calculation_set

    def test_store_file_info(self, service, session_manager_mock, stats_repository_mock):
        """Test store_file_info method stores a MoleculeSetStats object."""

        molecule_set_stats = MoleculeSetStats(
            {
                "total_molecules": 10,
                "total_atoms": 100,
                "atom_type_counts": [
                    {"symbol": "C", "count": 50},
                    {"symbol": "H", "count": 30},
                    {"symbol": "O", "count": 20},
                ],
            }
        )

        stats_repository_mock.store.return_value = molecule_set_stats

        result = service.store_file_info("hash123", molecule_set_stats)

        assert stats_repository_mock.store.call_count == 1
        store_arg = stats_repository_mock.store.call_args[0][1]
        assert store_arg.file_hash == "hash123"
        assert store_arg.total_molecules == 10
        assert store_arg.total_atoms == 100
        assert len(store_arg.atom_type_counts) == 3
        assert result == molecule_set_stats

    def test_store_calculation_results_new_set(
        self,
        service,
        session_manager_mock,
        set_repository_mock,
        calculation_repository_mock,
        advanced_settings_repository_mock,
        config_repository_mock,
        stats_repository_mock,
        sample_advanced_settings,
        sample_advanced_settings_entity,
        sample_calculation_result,
        sample_calculation_config_entity,
    ):
        """Test store_calculation_results method stores a new calculation set."""

        session = session_manager_mock.session().__enter__()

        set_repository_mock.get.return_value = None
        advanced_settings_repository_mock.get.return_value = sample_advanced_settings_entity
        config_repository_mock.get.return_value = sample_calculation_config_entity
        stats_repository_mock.get.return_value = MoleculeSetStatsModel(
            file_hash="hash123", total_molecules=10, total_atoms=100, atom_type_counts=[]
        )
        calculation_repository_mock.get.return_value = None

        service.store_calculation_results(
            "d55a7af3-d1ee-4884-bce0-805efd5e1e64",
            sample_advanced_settings,
            [sample_calculation_result],
            "user123",
        )

        set_repository_mock.get.assert_called_once_with(
            session, "d55a7af3-d1ee-4884-bce0-805efd5e1e64"
        )
        advanced_settings_repository_mock.get.assert_called_once()
        config_repository_mock.get.assert_called_once_with(session, "method1", "params1")
        assert set_repository_mock.store.call_count == 2
        assert calculation_repository_mock.store.call_count == 1

        calc_arg = calculation_repository_mock.store.call_args[0][1]
        assert calc_arg.file_name == "file1.mol"
        assert calc_arg.file_hash == "hash123"
        assert calc_arg.config == sample_calculation_config_entity

    def test_store_calculation_results_existing_set(
        self,
        service,
        session_manager_mock,
        set_repository_mock,
        calculation_repository_mock,
        advanced_settings_repository_mock,
        config_repository_mock,
        stats_repository_mock,
        sample_advanced_settings,
        sample_advanced_settings_entity,
        sample_calculation_result,
        sample_calculation_config_entity,
        sample_calculation_set,
    ):
        """Test store_calculation_results method updates an existing calculation set."""

        session = session_manager_mock.session().__enter__()

        set_repository_mock.get.return_value = sample_calculation_set
        advanced_settings_repository_mock.get.return_value = sample_advanced_settings_entity
        config_repository_mock.get.return_value = sample_calculation_config_entity
        stats_repository_mock.get.return_value = MoleculeSetStatsModel(
            file_hash="hash123", total_molecules=10, total_atoms=100, atom_type_counts=[]
        )
        calculation_repository_mock.get.return_value = None

        service.store_calculation_results(
            "d55a7af3-d1ee-4884-bce0-805efd5e1e64",
            sample_advanced_settings,
            [sample_calculation_result],
            "user123",
        )

        set_repository_mock.get.assert_called_once_with(
            session, "d55a7af3-d1ee-4884-bce0-805efd5e1e64"
        )
        set_repository_mock.store.assert_called_once_with(session, sample_calculation_set)
        assert calculation_repository_mock.store.call_count == 1

    def test_setup_calculation(
        self,
        service,
        session_manager_mock,
        set_repository_mock,
        advanced_settings_repository_mock,
        stats_repository_mock,
        sample_advanced_settings,
        sample_advanced_settings_entity,
    ):
        """Test setup_calculation method creates a new calculation set."""

        session = session_manager_mock.session().__enter__()
        advanced_settings_repository_mock.get.return_value = sample_advanced_settings_entity
        stats_repository_mock.get.return_value = MoleculeSetStatsModel(
            file_hash="hash123", total_molecules=10, total_atoms=100, atom_type_counts=[]
        )

        service.setup_calculation(
            "d55a7af3-d1ee-4884-bce0-805efd5e1e64", sample_advanced_settings, ["hash123"], "user123"
        )

        advanced_settings_repository_mock.get.assert_called_once()
        stats_repository_mock.get.assert_called_once_with(session, "hash123")
        set_repository_mock.store.assert_called_once()

        calc_set_arg = set_repository_mock.store.call_args[0][1]
        assert calc_set_arg.id == "d55a7af3-d1ee-4884-bce0-805efd5e1e64"
        assert calc_set_arg.user_id == "user123"
        assert calc_set_arg.advanced_settings == sample_advanced_settings_entity
        assert len(calc_set_arg.molecule_set_stats) == 1

    def test_filter_existing_calculations(
        self,
        service,
        session_manager_mock,
        calculation_repository_mock,
        sample_advanced_settings,
        sample_calculation_config,
    ):
        """Test filter_existing_calculations method correctly filters calculations."""

        # for the first file+config combination, return None (not in DB)
        # for the second file+config combination, return an existing calculation
        def mock_get_side_effect(session, filters):
            if filters.hash == "hash123":
                return None
            else:
                calculation = Calculation(
                    file_name="file2.mol",
                    file_hash="hash456",
                    charges={},
                    config=CalculationConfig(method="method1", parameters="params1"),
                    advanced_settings=AdvancedSettings(
                        read_hetatm=True, ignore_water=False, permissive_types=True
                    ),
                )
                return calculation

        calculation_repository_mock.get.side_effect = mock_get_side_effect

        to_calculate, cached = service.filter_existing_calculations(
            sample_advanced_settings, ["hash123", "hash456"], [sample_calculation_config]
        )

        assert len(to_calculate) == 1
        assert sample_calculation_config in to_calculate
        assert to_calculate[sample_calculation_config] == ["hash123"]

        assert len(cached) == 1
        assert sample_calculation_config in cached
        assert len(cached[sample_calculation_config]) == 1
        assert cached[sample_calculation_config][0].file_hash == "hash456"

    def test_get_calculation_results_not_found(
        self, service, session_manager_mock, set_repository_mock
    ):
        """Test get_calculation_results method returns an empty list when no value is found."""

        session = session_manager_mock.session().__enter__()
        set_repository_mock.get.return_value = None

        results = service.get_calculation_results("nonexistent")

        set_repository_mock.get.assert_called_once_with(session, "nonexistent")
        assert results == []

    def test_delete_calculation_set(self, service, session_manager_mock, set_repository_mock):
        """Test delete_calculation_set method deletes a calculation_set."""

        session = session_manager_mock.session().__enter__()

        service.delete_calculation_set("d55a7af3-d1ee-4884-bce0-805efd5e1e64")

        set_repository_mock.delete.assert_called_once_with(
            session, "d55a7af3-d1ee-4884-bce0-805efd5e1e64"
        )
