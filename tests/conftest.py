import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.core.auth.jwt import get_current_user
from src.api.core.database.database import Base, get_db
from src.api.core.security import create_access_token
from src.api.main import app

# --- AJOUT PYTHONPATH en premier ---
# Ajouter le répertoire src au PYTHONPATH pour les imports
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from fastapi.testclient import TestClient

# --- Config base SQLite pour tests ---
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Créer le moteur de base de données de test
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Créer la session de test
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Crée une session de base de données de test pour chaque test.
    """
    # Créer les tables
    Base.metadata.create_all(bind=test_engine)

    # Créer une session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Nettoyer les tables après chaque test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Crée un client de test FastAPI avec une base de données de test.
    """

    # Override de la dépendance get_db pour utiliser la session de test
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # Override de la dépendance get_current_user pour les tests
    def override_get_current_user():
        return {"id": 1, "username": "test_user"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    # Nettoyer les overrides
    app.dependency_overrides.clear()
