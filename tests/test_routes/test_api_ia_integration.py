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
