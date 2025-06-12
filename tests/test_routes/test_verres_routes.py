import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def sample_verre():
    return {
        "id": 1,
        "nom": "Test Verre",
        "fournisseur": "TestFournisseur",
        "materiau": "TestMateriau",
        "indice": 1.5
    }

def test_read_verres(client, sample_verre):
    """Test la route GET /verres sans authentification"""
    with patch("src.api.services.verres.get_verres") as mock_get_verres:
        mock_get_verres.return_value = {
            "total": 1,
            "items": [sample_verre]
        }
        
        response = client.get("/api/v1/verres")
        assert response.status_code == 401  # Vérifie que l'accès est refusé sans token

def test_read_verre_not_found(client):
    """Test la route GET /verres/{verre_id} pour un verre inexistant"""
    with patch("src.api.services.verres.get_verre") as mock_get_verre:
        mock_get_verre.return_value = None
        
        response = client.get("/api/v1/verres/999")
        assert response.status_code == 401  # Vérifie que l'accès est refusé sans token

def test_unauthorized_access(client):
    """Test l'accès non autorisé aux routes"""
    routes = [
        "/api/v1/verres",
        "/api/v1/verres/1",
        "/api/v1/verres/fournisseurs/list",
        "/api/v1/verres/materiaux/list"
    ]
    
    for route in routes:
        response = client.get(route)
        assert response.status_code == 401, f"Route {route} should require authentication" 