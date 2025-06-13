"""Tests de base de l'API."""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root():
    """Test la route racine de l'API."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API de gestion des verres optiques"}
