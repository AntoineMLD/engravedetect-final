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
    config.addinivalue_line(
        "markers", "torch: Tests nécessitant PyTorch/TorchVision"
    )
    config.addinivalue_line(
        "markers", "skip_torch: Tests à skiper si PyTorch non disponible"
    )


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
    
    # Base de données de test en mémoire
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers():
    """Fixture pour les headers d'authentification"""
    if not API_AVAILABLE:
        pytest.skip("API principale non disponible")
    
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Créer un token de test
    test_user = {"sub": "test@example.com", "exp": 9999999999}
    token = create_access_token(data=test_user)
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    """Fixture pour le client de test FastAPI"""
    if not API_AVAILABLE:
        pytest.skip("API principale non disponible")
    
    from fastapi.testclient import TestClient
    return TestClient(app)
