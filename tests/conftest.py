import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Configure l'environnement de test avec des variables d'environnement factices."""
    # Sauvegarde des variables d'environnement existantes
    original_env = dict(os.environ)

    # Configuration des variables d'environnement pour les tests
    test_env = {
        "DATABASE_URL": "sqlite:///./test.db",
        "AZURE_SERVER": "test-server",
        "AZURE_DATABASE": "test-db",
        "AZURE_USERNAME": "test-user",
        "AZURE_PASSWORD": "test-password",
        "SECRET_KEY": "test-secret-key-for-testing-only",
    }

    os.environ.update(test_env)

    yield

    # Restauration des variables d'environnement d'origine
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
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


@pytest.fixture
def test_client():
    """Crée un client de test pour l'application FastAPI."""
    return TestClient(app)
