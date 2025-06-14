import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.schemas.verres import VerreCreate, VerreUpdate
from src.api.models.verres import Verre


@pytest.fixture
def test_verre(db_session):
    """Crée un verre de test dans la base de données."""
    verre = Verre(
        nom="Test Verre",
        fournisseur="Test Fournisseur",
        materiaux="Test Materiaux",
        indice=1.5,
        protection=True,
        photochromic=False,
        hauteur_min=10.0,
        hauteur_max=20.0,
        gravure="TEST123",
    )
    db_session.add(verre)
    db_session.commit()
    db_session.refresh(verre)
    return verre


def test_verres_unauthorized(client):
    """Test d'accès non autorisé aux routes des verres."""
    # Suppression des dépendances d'authentification
    app.dependency_overrides = {}

    response = client.get("/api/v1/verres/")
    assert response.status_code == 401


def test_create_verre(client, auth_headers):
    """Test de création d'un verre."""
    verre_data = {
        "nom": "Test Verre",
        "fournisseur": "Test Fournisseur",
        "materiaux": "Test Materiaux",
        "indice": 1.5,
        "protection": True,
        "photochromic": False,
        "hauteur_min": 10.0,
        "hauteur_max": 20.0,
        "gravure": "TEST123",
    }

    response = client.post("/api/v1/verres/", json=verre_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == verre_data["nom"]
    assert data["fournisseur"] == verre_data["fournisseur"]


def test_create_verre_invalid_data(client, auth_headers):
    """Test de création d'un verre avec des données invalides."""
    verre_data = {
        "nom": "",  # Nom vide invalide
        "fournisseur": "Test Fournisseur",
        "materiaux": "Test Materiaux",
        "indice": -1,  # Indice négatif invalide
        "protection": True,
        "photochromic": False,
        "hauteur_min": 20.0,  # hauteur_min > hauteur_max
        "hauteur_max": 10.0,
        "gravure": "TEST123",
    }

    response = client.post("/api/v1/verres/", json=verre_data, headers=auth_headers)
    assert response.status_code == 422


def test_update_verre(client, auth_headers, test_verre):
    """Test de mise à jour d'un verre."""
    update_data = {"nom": "Updated Verre", "fournisseur": "Updated Fournisseur"}

    response = client.put(f"/api/v1/verres/{test_verre.id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nom"] == update_data["nom"]
    assert data["fournisseur"] == update_data["fournisseur"]


def test_update_verre_not_found(client, auth_headers):
    """Test de mise à jour d'un verre inexistant."""
    update_data = {"nom": "Updated Verre", "fournisseur": "Updated Fournisseur"}

    response = client.put("/api/v1/verres/999", json=update_data, headers=auth_headers)
    assert response.status_code == 404


def test_delete_verre(client, auth_headers, test_verre):
    """Test de suppression d'un verre."""
    response = client.delete(f"/api/v1/verres/{test_verre.id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_verre_not_found(client, auth_headers):
    """Test de suppression d'un verre inexistant."""
    response = client.delete("/api/v1/verres/999", headers=auth_headers)
    assert response.status_code == 404


def test_get_verres(client, auth_headers, test_verre):
    """Test de récupération de la liste des verres."""
    response = client.get("/api/v1/verres/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_verre_by_id(client, auth_headers, test_verre):
    """Test de récupération d'un verre par son ID."""
    response = client.get(f"/api/v1/verres/{test_verre.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_verre.id
    assert data["nom"] == test_verre.nom


def test_get_verre_by_id_not_found(client, auth_headers):
    """Test de récupération d'un verre inexistant."""
    response = client.get("/api/v1/verres/999", headers=auth_headers)
    assert response.status_code == 404


def test_get_verres_with_filters(client, auth_headers, test_verre):
    """Test de récupération des verres avec filtres."""
    filters = {"fournisseur": "Test Fournisseur", "indice_min": 1.0, "indice_max": 2.0, "protection": True}

    response = client.get("/api/v1/verres/", params=filters, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
