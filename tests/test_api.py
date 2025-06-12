from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_read_verres():
    response = client.get("/api/v1/verres")
    assert response.status_code == 401  # Unauthorized without token

def test_read_fournisseurs():
    response = client.get("/api/v1/verres/fournisseurs/list")
    assert response.status_code == 401  # Unauthorized without token 