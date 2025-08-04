import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- AJOUT PYTHONPATH en premier ---
# Ajouter le répertoire src au PYTHONPATH pour les imports
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from fastapi.testclient import TestClient

# Import conditionnel pour éviter les conflits avec l'API IA
try:
    from src.api.core.auth.jwt import get_current_user
    from src.api.core.database.database import Base, get_db
    from src.api.core.security import create_access_token
    from src.api.main import app

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

import pytest


def pytest_configure(config):
    """Configuration pytest pour les marqueurs personnalisés"""
    config.addinivalue_line("markers", "torch: Tests nécessitant PyTorch/TorchVision")
    config.addinivalue_line("markers", "skip_torch: Tests à skiper si PyTorch non disponible")


def check_torch_availability():
    """Vérifie si PyTorch et TorchVision sont disponibles et compatibles"""
    try:
        import torch
        import torchvision
        from torchvision import models

        # Test simple de compatibilité
        model = models.efficientnet_b0(weights=None)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def torch_available():
    """Fixture pour vérifier la disponibilité de PyTorch"""
    return check_torch_availability()


# Fixtures existantes avec vérification de disponibilité
@pytest.fixture
def db_session():
    """Fixture pour la session de base de données"""
    if not API_AVAILABLE:
        pytest.skip("API principale non disponible")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import tempfile
    import os

    # Utiliser un fichier temporaire au lieu de :memory: pour éviter les problèmes de threads
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    try:
        engine = create_engine(f"sqlite:///{temp_db.name}")
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Créer les tables
        Base.metadata.create_all(bind=engine)

        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)
    finally:
        # Nettoyer le fichier temporaire
        try:
            os.unlink(temp_db.name)
        except OSError:
            pass


@pytest.fixture
def client(db_session):
    """Fixture pour le client de test FastAPI avec base de données configurée"""
    if not API_AVAILABLE:
        pytest.skip("API principale non disponible")

    from fastapi.testclient import TestClient

    # Override de la dépendance get_db pour utiliser la session de test
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # La session est gérée par la fixture db_session

    # Override de la dépendance get_current_user pour les tests
    def override_get_current_user():
        return {"id": 1, "username": "test_user", "email": "test@example.com"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    # Nettoyer les overrides
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Fixture pour les headers d'authentification"""
    if not API_AVAILABLE:
        pytest.skip("API principale non disponible")

    # Créer un token de test
    test_user = {"sub": "test@example.com", "exp": 9999999999}
    token = create_access_token(data=test_user)

    return {"Authorization": f"Bearer {token}"}
