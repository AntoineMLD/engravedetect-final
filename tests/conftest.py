import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.main import app
from src.api.core.database.database import Base, get_db
from src.api.core.auth.jwt import create_access_token
from src.api.core.auth.jwt import get_current_user


# Configuration de la base SQLite pour les tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ========================================
# 1. Configuration des variables d'env
# ========================================


@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
    """Configure les variables d'environnement pour les tests."""
    original_env = dict(os.environ)
    test_env = {
        "DATABASE_URL": SQLALCHEMY_TEST_DATABASE_URL,
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "AZURE_SERVER": "test-server",
        "AZURE_DATABASE": "test-db",
        "AZURE_USERNAME": "test-user",
        "AZURE_PASSWORD": "test-password",
        "deploy_ssh_key": "",
    }
    os.environ.update(test_env)
    yield
    os.environ.clear()
    os.environ.update(original_env)


# ========================================
# 2. Setup de la base de test
# ========================================
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Crée les tables une fois pour tous les tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ========================================
# 3. Session DB propre à chaque test
# ========================================
@pytest.fixture
def db_session():
    """Fournit une session SQLAlchemy pour les tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


# ========================================
# 4. Utilisateur de test
# ========================================
@pytest.fixture
def mock_current_user():
    """Utilisateur simulé pour l'authentification."""
    return {"sub": "test@example.com", "id": 1}


@pytest.fixture
def auth_headers(mock_current_user):
    """Crée les headers avec JWT valide."""
    token = create_access_token(mock_current_user)
    return {"Authorization": f"Bearer {token}"}


# ========================================
# 5. Client FastAPI avec dépendances injectées
# ========================================
@pytest.fixture
def client(db_session, mock_current_user):
    """Fournit un client de test FastAPI avec dépendances surchargées."""

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return mock_current_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
