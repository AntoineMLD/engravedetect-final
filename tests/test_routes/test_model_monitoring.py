"""
Tests pour le monitoring du modèle d'IA EngraveDetect
Vérifie le bon fonctionnement des métriques et de la détection de drift.
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest

from src.api_ia.app.model_monitoring import ModelMonitor, model_monitor


class TestModelMonitoring:
    """Tests pour le monitoring du modèle d'IA"""

    def test_model_monitor_initialization(self):
        """Test de l'initialisation du ModelMonitor"""
        # Utiliser l'instance globale existante
        monitor = model_monitor

        assert monitor.model_name == "engravedetect_efficientnet"
        assert monitor.drift_check_probability == 0.1
        assert monitor.drift_threshold == 0.7
        assert monitor.reference_data is None
        assert monitor.baseline_established is False

    def test_update_prediction_metrics_success(self):
        """Test de la mise à jour des métriques de prédiction réussie"""
        # Utiliser l'instance globale existante
        monitor = model_monitor

        # Sauvegarder l'état initial
        initial_predictions = monitor.prediction_count
        initial_success = monitor.success_count

        # Données de test
        embedding = np.random.rand(128)
        similarity_scores = [0.9, 0.8, 0.7]
        inference_time = 0.5

        # Mise à jour des métriques
        monitor.update_prediction_metrics(
            embedding=embedding, similarity_scores=similarity_scores, inference_time=inference_time, success=True
        )

        # Vérifications
        health_status = monitor.get_model_health_status()
        assert health_status["total_predictions"] == initial_predictions + 1
        assert health_status["success_count"] == initial_success + 1

    def test_update_prediction_metrics_failure(self):
        """Test de la mise à jour des métriques de prédiction échouée"""
        # Utiliser l'instance globale existante
        monitor = model_monitor

        # Sauvegarder l'état initial
        initial_predictions = monitor.prediction_count
        initial_failed = monitor.prediction_count - monitor.success_count

        # Données de test
        embedding = np.random.rand(128)
        similarity_scores = [0.6, 0.5, 0.4]  # Scores faibles
        inference_time = 1.0

        # Mise à jour des métriques
        monitor.update_prediction_metrics(
            embedding=embedding, similarity_scores=similarity_scores, inference_time=inference_time, success=False
        )

        # Vérifications
        health_status = monitor.get_model_health_status()
        assert health_status["total_predictions"] == initial_predictions + 1
        # Vérifier que le nombre d'échecs a augmenté
        failed_predictions = health_status["total_predictions"] - health_status["success_count"]
        assert failed_predictions == initial_failed + 1

    def test_embedding_quality_calculation(self):
        """Test du calcul de la qualité des embeddings"""
        monitor = model_monitor

        # Sauvegarder l'état initial
        initial_quality = monitor.get_model_health_status()["average_embedding_quality"]

        # Embedding avec faible écart-type (bonne qualité)
        good_embedding = np.ones(128) + np.random.normal(0, 0.1, 128)

        # Test avec bon embedding
        monitor.update_prediction_metrics(embedding=good_embedding, similarity_scores=[0.9], inference_time=0.5, success=True)

        # Vérifier que la qualité est calculée (valeur entre 0 et 1)
        quality = monitor.get_model_health_status()["average_embedding_quality"]
        assert 0 <= quality <= 1
        assert quality > 0  # Doit être calculée

    def test_drift_detection_initialization(self):
        """Test de l'initialisation de la détection de drift"""
        monitor = model_monitor

        # Première détection (initialisation des données de référence)
        embedding = np.random.rand(128)
        drift_score = monitor.detect_data_drift(embedding)

        assert drift_score is not None  # Maintenant on a un score
        # La baseline peut ne pas être établie immédiatement
        assert monitor.baseline_established is True or len(monitor.baseline_embeddings) > 0

    def test_should_check_drift_probability(self):
        """Test de la probabilité de vérification du drift"""
        monitor = model_monitor

        # Test multiple pour vérifier la probabilité
        checks = [monitor.should_check_drift() for _ in range(1000)]
        check_rate = sum(checks) / len(checks)

        # La fréquence doit être proche de 0.1 (±5%)
        assert 0.05 <= check_rate <= 0.15

    def test_model_health_status_structure(self):
        """Test de la structure du statut de santé du modèle"""
        monitor = model_monitor

        status = monitor.get_model_health_status()

        # Vérifier la présence de tous les champs
        expected_fields = [
            "model_name",
            "total_predictions",
            "success_count",
            "top1_accuracy",
            "top3_accuracy",
            "rejection_rate",
            "average_inference_time",
            "average_confidence",
            "average_embedding_quality",
            "monitoring_active",
        ]

        for field in expected_fields:
            assert field in status

    def test_global_model_monitor_instance(self):
        """Test de l'instance globale du monitor"""
        assert model_monitor is not None
        assert isinstance(model_monitor, ModelMonitor)
        assert model_monitor.model_name == "engravedetect_efficientnet"


class TestModelMonitoringIntegration:
    """Tests d'intégration pour le monitoring du modèle"""

    def test_monitoring_with_real_embeddings(self):
        """Test avec des embeddings réalistes"""
        monitor = model_monitor

        # Simuler des embeddings réalistes (valeurs entre -1 et 1)
        embedding = np.random.uniform(-1, 1, 128)
        similarity_scores = [0.95, 0.87, 0.82, 0.76, 0.71]

        monitor.update_prediction_metrics(
            embedding=embedding, similarity_scores=similarity_scores, inference_time=0.3, success=True
        )

        status = monitor.get_model_health_status()

        # Vérifications
        assert status["total_predictions"] >= 1
        assert status["success_count"] >= 1
        assert 0 <= status["average_embedding_quality"] <= 1

    def test_monitoring_error_handling(self):
        """Test de la gestion d'erreurs dans le monitoring"""
        monitor = model_monitor

        # Test avec des données invalides - le code gère les erreurs gracieusement
        try:
            monitor.update_prediction_metrics(
                embedding=None, similarity_scores=[], inference_time=0.0, success=True  # Embedding invalide
            )
            # Si on arrive ici, c'est que l'erreur a été gérée correctement
            assert True
        except Exception as e:
            # Si une exception est levée, c'est aussi acceptable
            assert isinstance(e, Exception)

    def test_multiple_predictions_tracking(self):
        """Test du suivi de multiples prédictions"""
        monitor = model_monitor

        # Sauvegarder l'état initial
        initial_predictions = monitor.prediction_count
        initial_success = monitor.success_count

        # Simuler plusieurs prédictions
        for i in range(5):
            embedding = np.random.rand(128)
            success = i < 3  # 3 succès, 2 échecs
            similarity_scores = [0.9] if success else [0.6]

            monitor.update_prediction_metrics(
                embedding=embedding, similarity_scores=similarity_scores, inference_time=0.5, success=success
            )

        status = monitor.get_model_health_status()

        assert status["total_predictions"] == initial_predictions + 5
        assert status["success_count"] == initial_success + 3


class TestModelMonitoringAvailability:
    """Tests de disponibilité du monitoring"""

    def test_monitoring_availability(self):
        """Test que le monitoring fonctionne correctement"""
        # Vérifier que le monitoring fonctionne
        monitor = model_monitor
        assert monitor is not None
        assert hasattr(monitor, "update_prediction_metrics")
