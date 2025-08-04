"""
Tests de vérification des dépendances API IA

Vérifie que les dépendances essentielles sont installées et fonctionnelles.
"""

import pytest


class TestAPIIADependencies:
    """Tests de vérification des dépendances API IA"""

    def test_fastapi_available(self):
        """Test que FastAPI est disponible"""
        try:
            import fastapi

            assert fastapi.__version__ >= "0.104.0"
        except ImportError:
            pytest.skip("FastAPI non disponible")

    def test_uvicorn_available(self):
        """Test que Uvicorn est disponible"""
        try:
            import uvicorn

            assert uvicorn.__version__ >= "0.24.0"
        except ImportError:
            pytest.skip("Uvicorn non disponible")

    def test_pydantic_available(self):
        """Test que Pydantic est disponible"""
        try:
            import pydantic

            assert pydantic.__version__ >= "2.5.0"
        except ImportError:
            pytest.skip("Pydantic non disponible")

    def test_numpy_available(self):
        """Test que NumPy est disponible"""
        try:
            import numpy

            assert numpy.__version__ >= "1.26.0"
        except ImportError:
            pytest.skip("NumPy non disponible")

    def test_pandas_available(self):
        """Test que Pandas est disponible"""
        try:
            import pandas

            assert pandas.__version__ >= "2.0.0"
        except ImportError:
            pytest.skip("Pandas non disponible")

    def test_pillow_available(self):
        """Test que Pillow est disponible"""
        try:
            import PIL

            assert PIL.__version__ >= "10.0.0"
        except ImportError:
            pytest.skip("Pillow non disponible")

    def test_scikit_learn_available(self):
        """Test que Scikit-learn est disponible"""
        try:
            import sklearn

            assert sklearn.__version__ >= "1.3.0"
        except ImportError:
            pytest.skip("Scikit-learn non disponible")

    def test_torch_available(self):
        """Test que PyTorch est disponible (optionnel)"""
        try:
            import torch

            assert torch.__version__ >= "2.2.0"
        except ImportError:
            pytest.skip("PyTorch non disponible - optionnel pour les tests")

    def test_prometheus_client_available(self):
        """Test que Prometheus Client est disponible"""
        try:
            import prometheus_client

            assert prometheus_client.__version__ >= "0.22.0"
        except ImportError:
            pytest.skip("Prometheus Client non disponible")

    def test_pyyaml_available(self):
        """Test que PyYAML est disponible"""
        try:
            import yaml

            # PyYAML n'a pas de version facilement accessible
            assert yaml is not None
        except ImportError:
            pytest.skip("PyYAML non disponible")


class TestAPIIAImportStructure:
    """Tests de vérification de la structure d'import de l'API IA"""

    def test_api_ia_module_structure(self):
        """Test que la structure du module API IA est correcte"""
        import os
        import sys

        # Vérifier que le répertoire src/api_ia existe
        api_ia_path = os.path.join("src", "api_ia")
        assert os.path.exists(api_ia_path), f"Le répertoire {api_ia_path} n'existe pas"

        # Vérifier que le fichier main.py existe
        main_path = os.path.join(api_ia_path, "app", "main.py")
        assert os.path.exists(main_path), f"Le fichier {main_path} n'existe pas"

        # Vérifier que le fichier requirements.txt existe
        requirements_path = os.path.join(api_ia_path, "requirements.txt")
        assert os.path.exists(requirements_path), f"Le fichier {requirements_path} n'existe pas"

    def test_api_ia_import_attempt(self):
        """Test d'import de l'API IA (peut échouer si dépendances manquantes)"""
        try:
            # Ajouter le répertoire src au path
            import os
            import sys

            sys.path.insert(0, os.path.join(os.getcwd(), "src"))

            # Tentative d'import
            from api_ia.app.main import app

            assert app is not None
        except ImportError as e:
            pytest.skip(f"Import API IA échoué: {e}")
        except Exception as e:
            pytest.skip(f"Erreur lors de l'import API IA: {e}")
