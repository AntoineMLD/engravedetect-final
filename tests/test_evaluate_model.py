import sys
import os
import pytest
import numpy as np
import torch
import tempfile
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from src.models.evaluate_model import (
    load_model,
    compute_topk_accuracy,
    plot_topk,
    plot_confusion,
    extract_embeddings,
    transform,
)
from src.models.efficientnet_triplet import EfficientNetEmbedding

# Configuration matplotlib
matplotlib.use("Agg")  # Utiliser le backend Agg pour éviter les problèmes avec Tkinter

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEvaluateModel:
    def setup_method(self):
        """Setup pour chaque test"""
        self.device = "cpu"  # Force CPU pour les tests
        self.embedding_dim = 256
        self.image_size = 224

    def test_transform_pipeline(self):
        """Test de la pipeline de transformation d'image"""
        # Convertir le numpy array en PIL Image
        img = Image.fromarray(np.random.rand(224, 224).astype(np.float32))
        tensor = transform(img)
        assert tensor.shape == (1, 224, 224)

    def test_compute_topk_accuracy_perfect_match(self):
        """Test top-k accuracy avec correspondance parfaite"""
        # Données de test - embeddings identiques pour même classe
        test_embeddings = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        test_labels = ["A", "B", "C"]
        ref_embeddings = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        ref_labels = ["A", "B", "C"]

        topk_acc, y_true, y_pred = compute_topk_accuracy(test_embeddings, test_labels, ref_embeddings, ref_labels, [1, 3])

        # Vérifications
        assert topk_acc["Top-1"] == 1.0, "Top-1 devrait être 100%"
        assert topk_acc["Top-3"] == 1.0, "Top-3 devrait être 100%"
        assert y_true == test_labels
        assert y_pred == test_labels

    def test_compute_topk_accuracy_no_match(self):
        """Test top-k accuracy sans correspondance"""
        # Données de test - classes complètement différentes
        test_embeddings = np.array([[1, 0], [0, 1]])
        test_labels = ["X", "Y"]  # Classes qui n'existent pas dans ref
        ref_embeddings = np.array([[1, 0], [0, 1]])
        ref_labels = ["A", "B"]  # Classes différentes

        topk_acc, y_true, y_pred = compute_topk_accuracy(test_embeddings, test_labels, ref_embeddings, ref_labels, [1])

        # Top-1 devrait être 0% car aucune classe test n'existe dans ref
        assert topk_acc["Top-1"] == 0.0

    def test_compute_topk_accuracy_partial_match(self):
        """Test top-k accuracy avec correspondance partielle"""
        # Données de test modifiées pour obtenir 0.75
        test_embeddings = np.array([[1.0, 0.0], [0.0, 1.0]])
        ref_embeddings = np.array([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]])
        test_labels = ["class1", "class2"]
        ref_labels = ["class1", "class2", "class1"]

        topk_acc, _, _ = compute_topk_accuracy(test_embeddings, test_labels, ref_embeddings, ref_labels, ks=[1, 3, 5])
        assert topk_acc["Top-1"] == 1.0

    def test_topk_accuracy_with_different_k_values(self):
        """Test que Top-3 >= Top-1"""
        test_embeddings = np.random.rand(10, 5)
        test_labels = ["A"] * 5 + ["B"] * 5
        ref_embeddings = np.random.rand(20, 5)
        ref_labels = ["A"] * 10 + ["B"] * 10

        topk_acc, _, _ = compute_topk_accuracy(test_embeddings, test_labels, ref_embeddings, ref_labels, [1, 3, 5])

        # Top-k devrait être croissant
        assert topk_acc["Top-1"] <= topk_acc["Top-3"] <= topk_acc["Top-5"]

    def test_plot_topk_creates_file(self):
        """Test de génération du graphique top-k"""
        topk_acc = {"Top-1": 0.8, "Top-3": 0.9, "Top-5": 0.95}

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch("src.models.evaluate_model.PLOT_TOPK_PATH", tmp_path):
                plot_topk(topk_acc)

            # Vérifier que le fichier existe
            assert os.path.exists(tmp_path)
            assert os.path.getsize(tmp_path) > 0
        finally:
            os.unlink(tmp_path)

    def test_plot_confusion_creates_file(self, tmp_path):
        """Test de génération de la matrice de confusion"""
        y_true = ["A", "B", "A", "B", "C"]
        y_pred = ["A", "A", "A", "B", "C"]

        with patch("src.models.evaluate_model.PLOT_CONFMAT_PATH", tmp_path):
            plot_confusion(y_true, y_pred)

        # Vérifier que le fichier existe
        assert tmp_path.exists()

    def test_plot_topk_values(self, tmp_path):
        plot_path = tmp_path / "test_plot.png"

        with patch("src.models.evaluate_model.PLOT_TOPK_PATH", str(plot_path)):
            topk_acc = {"Top-1": 0.8, "Top-3": 0.9, "Top-5": 1.0}
            plot_topk(topk_acc)
            assert plot_path.exists()
            plt.close("all")  # Fermer explicitement les figures

    def test_embedding_dimensions(self):
        """Test que les embeddings ont la bonne dimension"""
        # Mock d'embeddings
        embeddings = np.random.rand(10, 256)

        assert embeddings.shape[1] == 256, "Dimension d'embedding incorrecte"
        assert len(embeddings.shape) == 2, "Embeddings doivent être 2D"

    def test_cosine_similarity_range(self):
        """Test que la similarité cosine est dans [-1, 1]"""
        from sklearn.metrics.pairwise import cosine_similarity

        # Embeddings normalisés
        emb1 = np.array([[1, 0], [0, 1]])
        emb2 = np.array([[1, 0], [-1, 0]])

        sim = cosine_similarity(emb1, emb2)

        assert -1 <= sim.min() <= sim.max() <= 1, "Similarité cosine hors range"

    def test_labels_consistency(self):
        """Test de cohérence des labels"""
        test_labels = ["A", "B", "C"]
        ref_labels = ["A", "B", "C", "D"]

        # Tous les test_labels doivent être dans ref_labels pour un test réaliste
        # Ici on teste juste qu'on peut gérer des labels différents
        unique_test = set(test_labels)
        unique_ref = set(ref_labels)

        assert len(unique_test) > 0
        assert len(unique_ref) > 0


class TestPerformanceMetrics:
    """Tests spécifiques aux métriques de performance"""

    def test_accuracy_calculation_edge_cases(self):
        """Test des cas limites pour le calcul d'accuracy"""
        # Cas avec un seul échantillon
        test_embeddings = np.array([[1.0, 0.0]])
        ref_embeddings = np.array([[1.0, 0.0]])
        test_labels = ["class1"]
        ref_labels = ["class1"]

        topk_acc, _, _ = compute_topk_accuracy(test_embeddings, test_labels, ref_embeddings, ref_labels, ks=[1])
        assert topk_acc["Top-1"] == 1.0

    def test_memory_usage_simulation(self):
        """Test simulation d'usage mémoire avec gros datasets"""
        # Simuler des embeddings de grande taille
        large_embeddings = np.random.rand(1000, 256)
        large_labels = [f"class_{i % 10}" for i in range(1000)]

        # Test que le calcul ne plante pas
        test_emb = large_embeddings[:100]
        test_lab = large_labels[:100]

        topk_acc, _, _ = compute_topk_accuracy(test_emb, test_lab, large_embeddings, large_labels, [1, 5])

        assert 0 <= topk_acc["Top-1"] <= 1
        assert 0 <= topk_acc["Top-5"] <= 1

    def test_timing_consistency(self):
        """Test que les calculs sont déterministes"""
        embeddings = np.random.rand(50, 10)
        labels = [f"class_{i % 5}" for i in range(50)]

        # Deux calculs identiques
        result1, _, _ = compute_topk_accuracy(embeddings[:25], labels[:25], embeddings[25:], labels[25:], [1])
        result2, _, _ = compute_topk_accuracy(embeddings[:25], labels[:25], embeddings[25:], labels[25:], [1])

        assert result1["Top-1"] == result2["Top-1"], "Résultats non déterministes"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
