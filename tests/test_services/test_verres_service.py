import pytest
from unittest.mock import Mock, patch
from src.api.services import verres as verres_service

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_data_cleaner():
    mock = Mock()
    mock.DEFAULTS = Mock()
    return mock

@pytest.fixture
def sample_verre():
    return Mock(
        id=1,
        nom="Test Verre",
        fournisseur="TestFournisseur",
        materiau="TestMateriau",
        indice=1.5
    )

def test_get_verre_by_id(mock_db, sample_verre, mock_data_cleaner):
    """Test la récupération d'un verre par ID"""
    with patch("src.api.services.verres.DataCleaner", mock_data_cleaner):
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_verre

        result = verres_service.get_verre(mock_db, verre_id=1)
        assert result == sample_verre

def test_get_verre_not_found(mock_db, mock_data_cleaner):
    """Test la récupération d'un verre inexistant"""
    with patch("src.api.services.verres.DataCleaner", mock_data_cleaner):
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = verres_service.get_verre(mock_db, verre_id=999)
        assert result is None 