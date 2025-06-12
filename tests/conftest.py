import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def mock_settings():
    """Mock les settings pour les tests."""
    with patch("src.api.core.config.Settings") as mock_settings:
        mock_settings.return_value.DATABASE_URL = "sqlite:///./test.db"
        mock_settings.return_value.SECRET_KEY = "test_key"
        mock_settings.return_value.AZURE_SERVER = "test_server"
        mock_settings.return_value.AZURE_DATABASE = "test_db"
        mock_settings.return_value.AZURE_USERNAME = "test_user"
        mock_settings.return_value.AZURE_PASSWORD = "test_pass"
        yield mock_settings

@pytest.fixture
def mock_db():
    """Mock de la session de base de données."""
    return MagicMock()

@pytest.fixture
def client(mock_db):
    """Client de test avec base de données mockée."""
    from src.api.main import app
    from src.api.core.database.database import get_db
    
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear() 