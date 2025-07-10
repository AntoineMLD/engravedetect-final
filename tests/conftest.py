import os
import sys
import pytest

# --- AJOUT PYTHONPATH en premier ---
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.api.core.database.database import Base, get_db
from src.api.core.security import create_access_token 
from src.api.core.auth.jwt import get_current_user

# --- Config base SQLite pour tests ---
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 1. Configuration variables d'env pour tests ---
@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
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

# --- 2. Création / destruction de la base ---
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- 3. Session DB isolée par test ---
@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

# --- 4. Utilisateur simulé ---
@pytest.fixture
def mock_current_user():
    return {"sub": "test@example.com", "id": 1}

# --- 5. Headers d'authentification ---
@pytest.fixture
def auth_headers(mock_current_user):
    token = create_access_token(mock_current_user)
    return {"Authorization": f"Bearer {token}"}

# --- 6. Client FastAPI avec overrides ---
@pytest.fixture
def client(db_session, mock_current_user):

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return mock_current_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
