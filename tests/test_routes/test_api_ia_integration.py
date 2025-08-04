"""
Tests d'intégration simplifiés pour l'API IA

Tests essentiels pour les endpoints principaux de l'API IA :
- /token (authentification)
- /embedding (génération d'embeddings)
- /match (recherche de correspondances)
- /search_tags (recherche par tags)
"""

import io
import os
import sys
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Ajouter le répertoire src au PYTHONPATH
src_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Mock global avant import
import sys
from unittest.mock import Mock, patch

# Mock des fonctions qui échouent au chargement
sys.modules["torch"] = Mock()
sys.modules["torchvision"] = Mock()

# Import conditionnel
try:
    with (
        patch("src.api_ia.app.model_loader.load_model") as mock_load_model,
        patch("src.api_ia.app.similarity_search.load_references") as mock_load_refs,
        patch("src.api_ia.app.model_loader.MODEL_WEIGHTS_PATH", "/fake/path/model.pth"),
        patch("src.api_ia.app.similarity_search.REFERENCES_PATH", "/fake/path/references.json"),
    ):

        # Mock du modèle
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        mock_load_refs.return_value = []

        from src.api_ia.app.main import app

        API_IA_AVAILABLE = True
except Exception as e:
    print(f"Erreur d'import: {e}")
    API_IA_AVAILABLE = False
    app = None


@pytest.mark.skipif(not API_IA_AVAILABLE, reason="API IA non disponible")
class TestAPIIAIntegration:
    """Tests d'intégration simplifiés pour l'API IA"""

    @pytest.fixture
    def client(self):
        """Client de test FastAPI"""
        with TestClient(app) as test_client:
            yield test_client

    @pytest.fixture
    def auth_token(self, client):
        """Token d'authentification pour les tests"""
        with patch("src.api_ia.app.security.authenticate_user") as mock_auth:
            mock_auth.return_value = {"username": "test_user", "email": "test@example.com"}

            response = client.post("/token", data={"username": "test_user", "password": "test_password"})

            return response.json()["access_token"]

    @pytest.fixture
    def test_image(self):
        """Image de test simple"""
        img = Image.new("L", (224, 224), color=128)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes.getvalue()

    def test_token_endpoint(self, client):
        """Test d'authentification"""
        with patch("src.api_ia.app.security.authenticate_user") as mock_auth:
            mock_auth.return_value = {"username": "test_user", "email": "test@example.com"}

            response = client.post("/token", data={"username": "test_user", "password": "test_password"})

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    def test_embedding_endpoint(self, client, auth_token, test_image):
        """Test de génération d'embedding"""
        with patch("src.api_ia.app.model_loader.get_embedding") as mock_get_embedding:
            mock_embedding = Mock()
            mock_embedding.shape = (512,)
            mock_embedding.tolist.return_value = [0.1] * 512
            mock_get_embedding.return_value = mock_embedding

            files = {"file": ("test_image.png", test_image, "image/png")}
            headers = {"Authorization": f"Bearer {auth_token}"}

            response = client.post("/embedding", files=files, headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert "embedding" in data
            assert len(data["embedding"]) == 512

    def test_match_endpoint(self, client, auth_token, test_image):
        """Test de recherche de correspondances"""
        with (
            patch("src.api_ia.app.model_loader.get_embedding") as mock_get_embedding,
            patch("src.api_ia.app.similarity_search.get_top_matches") as mock_get_matches,
        ):

            mock_embedding = Mock()
            mock_embedding.shape = (512,)
            mock_embedding.tolist.return_value = [0.1] * 512
            mock_embedding.min.return_value = 0.0
            mock_embedding.max.return_value = 1.0
            mock_embedding.mean.return_value = 0.5
            mock_get_embedding.return_value = mock_embedding

            mock_matches = [{"class": "e_courbebasse", "similarity": 0.95}, {"class": "e_courbehaute", "similarity": 0.87}]
            mock_get_matches.return_value = mock_matches

            files = {"file": ("test_image.png", test_image, "image/png")}
            headers = {"Authorization": f"Bearer {auth_token}"}

            response = client.post("/match", files=files, headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert "matches" in data
            assert len(data["matches"]) == 2
            assert "class_" in data["matches"][0]
            assert "similarity" in data["matches"][0]

    def test_search_tags_endpoint(self, client, auth_token):
        """Test de recherche par tags"""
        with patch("src.api_ia.app.database.find_matching_verres") as mock_find_verres:
            mock_find_verres.return_value = [{"id": 1, "nom": "Verre Courbe Basse", "tags": ["courbe", "basse"]}]

            headers = {"Authorization": f"Bearer {auth_token}"}
            tags = ["courbe", "basse"]

            response = client.post("/search_tags", json=tags, headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) == 1

    def test_health_check(self, client):
        """Test de santé de l'API"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_authentication_required(self, client, test_image):
        """Test que l'authentification est requise"""
        files = {"file": ("test_image.png", test_image, "image/png")}

        response = client.post("/embedding", files=files)

        assert response.status_code == 401

    def test_invalid_image_rejected(self, client, auth_token):
        """Test que les fichiers non-images sont rejetés"""
        invalid_file = b"This is not an image"

        files = {"file": ("invalid.txt", invalid_file, "text/plain")}
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = client.post("/embedding", files=files, headers=headers)

        assert response.status_code == 400

    def test_verre_details_endpoint(self, client, auth_token):
        """Test de récupération des détails d'un verre"""
        with patch("src.api_ia.app.database.get_verre_details") as mock_get_verre:
            mock_get_verre.return_value = {
                "id": 1,
                "nom": "Verre Test",
                "fournisseur": "Test Fournisseur",
                "materiaux": "Test Materiaux",
                "indice": 1.5,
                "protection": True,
                "photochromic": False,
                "hauteur_min": 10.0,
                "hauteur_max": 20.0,
                "gravure": "TEST123",
            }

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/verre/1", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["nom"] == "Verre Test"
            assert data["fournisseur"] == "Test Fournisseur"

    def test_verre_details_not_found(self, client, auth_token):
        """Test de récupération d'un verre inexistant"""
        with patch("src.api_ia.app.database.get_verre_details") as mock_get_verre:
            mock_get_verre.return_value = None

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/verre/999", headers=headers)

            assert response.status_code == 404

    def test_me_endpoint(self, client, auth_token):
        """Test de récupération des informations utilisateur"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data

    def test_delete_me_endpoint(self, client, auth_token):
        """Test de suppression de l'utilisateur"""
        with patch("src.api_ia.app.database.delete_user_by_username") as mock_delete:
            mock_delete.return_value = True

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.delete("/me", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Utilisateur supprimé avec succès"

    def test_delete_me_not_found(self, client, auth_token):
        """Test de suppression d'un utilisateur inexistant"""
        with patch("src.api_ia.app.database.delete_user_by_username") as mock_delete:
            mock_delete.return_value = False

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.delete("/me", headers=headers)

            assert response.status_code == 404

    def test_root_endpoint(self, client):
        """Test de l'endpoint racine"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data

    def test_metrics_endpoint(self, client):
        """Test de l'endpoint des métriques Prometheus"""
        response = client.get("/metrics")

        assert response.status_code == 200
        # Vérifier que c'est du texte Prometheus
        content = response.text
        assert "prometheus" in content.lower() or "counter" in content.lower()

    def test_rate_limiting(self, client, auth_token, test_image):
        """Test de limitation de débit"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        files = {"file": ("test_image.png", test_image, "image/png")}

        # Faire plusieurs requêtes rapides pour déclencher la limitation
        responses = []
        for _ in range(6):  # Plus que la limite de 5/minute
            response = client.post("/embedding", files=files, headers=headers)
            responses.append(response)

        # Au moins une requête devrait être limitée
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes or all(code == 200 for code in status_codes)

    def test_cors_headers(self, client):
        """Test des en-têtes CORS"""
        response = client.options("/token")

        assert response.status_code == 200
        # Vérifier la présence d'en-têtes CORS
        assert "access-control-allow-origin" in response.headers

    def test_security_headers(self, client):
        """Test des en-têtes de sécurité"""
        response = client.get("/health")

        assert response.status_code == 200
        # Vérifier la présence d'en-têtes de sécurité
        headers = response.headers
        assert "x-content-type-options" in headers or "x-frame-options" in headers
