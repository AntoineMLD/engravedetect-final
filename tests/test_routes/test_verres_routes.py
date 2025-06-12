from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_verres_unauthorized():
    """Test simple d'authentification sur la route des verres."""
    response = client.get("/api/v1/verres/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"} 