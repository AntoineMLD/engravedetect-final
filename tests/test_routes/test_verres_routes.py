import pytest
from fastapi.testclient import TestClient
from src.api.main import app

def test_verres_unauthorized():
    """Test d'accès non autorisé aux routes des verres."""
    client = TestClient(app)
    
    # Suppression des dépendances d'authentification
    app.dependency_overrides = {}
    
    response = client.get("/api/v1/verres/")
    assert response.status_code == 401
