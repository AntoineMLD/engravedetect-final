"""
Tests pour le monitoring du modèle d'IA EngraveDetect
Vérifie le bon fonctionnement des métriques et de la détection de drift.
"""

import numpy as np
import pytest
from unittest.mock import Mock, patch

from src.api_ia.app.model_monitoring import ModelMonitor, model_monitor


class TestModelMonitoring:
    """Tests pour le monitoring du modèle d'IA"""
    
    def test_model_monitor_initialization(self):
        """Test de l'initialisation du ModelMonitor"""
        monitor = ModelMonitor(embedding_dim=128)
        
        assert monitor.embedding_dim == 128
        assert monitor.confidence_threshold == 0.8
        assert monitor.drift_detection_frequency == 0.1
        assert monitor.reference_data is None
    
    def test_update_prediction_metrics_success(self):
        """Test de la mise à jour des métriques de prédiction réussie"""
        monitor = ModelMonitor()
        
        # Données de test
        embedding = np.random.rand(128)
        similarity_scores = [0.9, 0.8, 0.7]
        inference_time = 0.5
        
        # Mise à jour des métriques
        monitor.update_prediction_metrics(
            embedding=embedding,
            similarity_scores=similarity_scores,
            inference_time=inference_time,
            success=True
        )
        
        # Vérifications
        assert monitor.get_model_health_status()["model_accuracy"] == 1.0  # 0.9 > 0.8
        assert monitor.get_model_health_status()["total_predictions"] == 1
        assert monitor.get_model_health_status()["successful_predictions"] == 1
        assert monitor.get_model_health_status()["failed_predictions"] == 0
    
    def test_update_prediction_metrics_failure(self):
        """Test de la mise à jour des métriques de prédiction échouée"""
        monitor = ModelMonitor()
        
        # Données de test
        embedding = np.random.rand(128)
        similarity_scores = [0.6, 0.5, 0.4]  # Scores faibles
        inference_time = 1.0
        
        # Mise à jour des métriques
        monitor.update_prediction_metrics(
            embedding=embedding,
            similarity_scores=similarity_scores,
            inference_time=inference_time,
            success=False
        )
        
        # Vérifications
        assert monitor.get_model_health_status()["model_accuracy"] == 0.0  # 0.6 < 0.8
        assert monitor.get_model_health_status()["failed_predictions"] == 1
    
    def test_embedding_quality_calculation(self):
        """Test du calcul de la qualité des embeddings"""
        monitor = ModelMonitor()
        
        # Embedding avec faible écart-type (bonne qualité)
        good_embedding = np.ones(128) + np.random.normal(0, 0.1, 128)
        
        # Embedding avec fort écart-type (mauvaise qualité)
        bad_embedding = np.random.normal(0, 1.0, 128)
        
        # Test avec bon embedding
        monitor.update_prediction_metrics(
            embedding=good_embedding,
            similarity_scores=[0.9],
            inference_time=0.5,
            success=True
        )
        
        good_quality = monitor.get_model_health_status()["model_embedding_quality"]
        
        # Test avec mauvais embedding
        monitor.update_prediction_metrics(
            embedding=bad_embedding,
            similarity_scores=[0.9],
            inference_time=0.5,
            success=True
        )
        
        bad_quality = monitor.get_model_health_status()["model_embedding_quality"]
        
        # La qualité du bon embedding doit être supérieure
        assert good_quality > bad_quality
    
    def test_drift_detection_initialization(self):
        """Test de l'initialisation de la détection de drift"""
        monitor = ModelMonitor()
        
        # Première détection (initialisation des données de référence)
        embedding = np.random.rand(128)
        drift_score = monitor.detect_data_drift(embedding)
        
        assert drift_score is None  # Première fois, pas de score
        assert monitor.reference_data is not None
    
    @patch('src.api_ia.app.model_monitoring.Report')
    def test_drift_detection_with_reference(self, mock_report):
        """Test de la détection de drift avec données de référence"""
        monitor = ModelMonitor()
        
        # Initialiser les données de référence
        reference_embedding = np.random.rand(128)
        monitor.detect_data_drift(reference_embedding)
        
        # Mock du rapport Evidently
        mock_report_instance = Mock()
        mock_report_instance.metrics = [Mock()]
        mock_report_instance.metrics[0].result.drift_score = 0.8
        mock_report.return_value = mock_report_instance
        
        # Détection de drift
        current_embedding = np.random.rand(128)
        drift_score = monitor.detect_data_drift(current_embedding)
        
        assert drift_score == 0.8
        mock_report.assert_called_once()
    
    def test_should_check_drift_probability(self):
        """Test de la probabilité de vérification du drift"""
        monitor = ModelMonitor()
        monitor.drift_detection_frequency = 0.5  # 50%
        
        # Test multiple pour vérifier la probabilité
        checks = [monitor.should_check_drift() for _ in range(1000)]
        check_rate = sum(checks) / len(checks)
        
        # La fréquence doit être proche de 0.5 (±10%)
        assert 0.4 <= check_rate <= 0.6
    
    def test_model_health_status_structure(self):
        """Test de la structure du statut de santé du modèle"""
        monitor = ModelMonitor()
        
        status = monitor.get_model_health_status()
        
        # Vérifier la présence de tous les champs
        expected_fields = [
            "model_accuracy", "model_drift_score", "model_embedding_quality",
            "total_predictions", "successful_predictions", "failed_predictions",
            "confidence_threshold", "drift_detection_frequency"
        ]
        
        for field in expected_fields:
            assert field in status
    
    def test_global_model_monitor_instance(self):
        """Test de l'instance globale du monitor"""
        assert model_monitor is not None
        assert isinstance(model_monitor, ModelMonitor)
        assert model_monitor.embedding_dim == 128


class TestModelMonitoringIntegration:
    """Tests d'intégration pour le monitoring du modèle"""
    
    def test_monitoring_with_real_embeddings(self):
        """Test avec des embeddings réalistes"""
        monitor = ModelMonitor()
        
        # Simuler des embeddings réalistes (valeurs entre -1 et 1)
        embedding = np.random.uniform(-1, 1, 128)
        similarity_scores = [0.95, 0.87, 0.82, 0.76, 0.71]
        
        monitor.update_prediction_metrics(
            embedding=embedding,
            similarity_scores=similarity_scores,
            inference_time=0.3,
            success=True
        )
        
        status = monitor.get_model_health_status()
        
        # Vérifications
        assert status["model_accuracy"] == 1.0  # 0.95 > 0.8
        assert status["total_predictions"] == 1
        assert status["successful_predictions"] == 1
        assert 0 <= status["model_embedding_quality"] <= 1
    
    def test_monitoring_error_handling(self):
        """Test de la gestion d'erreurs dans le monitoring"""
        monitor = ModelMonitor()
        
        # Test avec des données invalides
        with pytest.raises(Exception):
            monitor.update_prediction_metrics(
                embedding=None,  # Embedding invalide
                similarity_scores=[],
                inference_time=0.0,
                success=True
            )
    
    def test_multiple_predictions_tracking(self):
        """Test du suivi de multiples prédictions"""
        monitor = ModelMonitor()
        
        # Simuler plusieurs prédictions
        for i in range(5):
            embedding = np.random.rand(128)
            success = i < 3  # 3 succès, 2 échecs
            similarity_scores = [0.9] if success else [0.6]
            
            monitor.update_prediction_metrics(
                embedding=embedding,
                similarity_scores=similarity_scores,
                inference_time=0.5,
                success=success
            )
        
        status = monitor.get_model_health_status()
        
        assert status["total_predictions"] == 5
        assert status["successful_predictions"] == 3
        assert status["failed_predictions"] == 2


class TestModelMonitoringAvailability:
    """Tests de disponibilité du monitoring"""
    
    def test_monitoring_availability(self):
        """Test que le monitoring fonctionne correctement"""
        # Vérifier que le monitoring fonctionne
        monitor = ModelMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'update_prediction_metrics') 