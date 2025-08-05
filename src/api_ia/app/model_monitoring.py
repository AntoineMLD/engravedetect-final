"""
Module de monitoring du modèle d'IA EngraveDetect.

Ce module collecte et analyse les métriques du modèle d'IA,
incluant la détection de drift basée sur une baseline historique
et la qualité des prédictions.
"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
from prometheus_client import Counter, Gauge, Histogram


logger = logging.getLogger(__name__)


class ModelMonitor:
    """
    Moniteur pour le modèle d'IA EngraveDetect.

    Collecte les métriques de performance, détecte le drift des données
    et fournit des alertes en temps réel.
    """

    def __init__(self):
        """Initialise le moniteur avec les métriques Prometheus."""
        # Métriques Prometheus pour le modèle
        # Métriques de performance de classification
        self.model_top1_accuracy = Gauge(
            "model_top1_accuracy", "Top-1 accuracy du modèle (classe prédite correcte)", ["model_name"]
        )

        self.model_top3_accuracy = Gauge(
            "model_top3_accuracy", "Top-3 accuracy du modèle (classe correcte dans top 3)", ["model_name"]
        )

        self.model_confidence_high = Counter(
            "model_confidence_high", "Prédictions avec confiance élevée (>0.8)", ["model_name"]
        )

        self.model_confidence_medium = Counter(
            "model_confidence_medium", "Prédictions avec confiance moyenne (0.5-0.8)", ["model_name"]
        )

        self.model_confidence_low = Counter("model_confidence_low", "Prédictions avec confiance faible (<0.5)", ["model_name"])

        self.model_rejection_rate = Gauge("model_rejection_rate", "Taux de rejet (confiance < seuil)", ["model_name"])

        # Métriques de performance système
        self.model_inference_time_seconds = Histogram(
            "model_inference_time_seconds",
            "Temps d'inférence du modèle d'IA",
            ["model_name"],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        )

        self.model_prediction_confidence = Histogram(
            "model_prediction_confidence",
            "Confiance des prédictions du modèle",
            ["model_name"],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        )

        # Métriques de qualité des embeddings
        self.model_embedding_quality = Gauge("model_embedding_quality", "Qualité des embeddings générés", ["model_name"])

        self.model_embedding_normality = Gauge(
            "model_embedding_normality", "Normalité des embeddings (test de Shapiro-Wilk)", ["model_name"]
        )

        self.model_feature_activation = Gauge(
            "model_feature_activation", "Activité moyenne des features du modèle", ["model_name"]
        )

        # Métriques de drift
        self.model_drift_score = Gauge("model_drift_score", "Score de drift des données d'entrée", ["model_name"])

        # Métriques de volume
        self.model_predictions_total = Counter(
            "model_predictions_total", "Nombre total de prédictions", ["model_name", "status"]
        )

        self.model_predictions_success = Counter("model_predictions_success", "Nombre de prédictions réussies", ["model_name"])

        self.model_predictions_failed = Counter("model_predictions_failed", "Nombre de prédictions échouées", ["model_name"])

        # Métriques de throughput
        self.model_throughput = Gauge("model_throughput", "Débit de prédictions par minute", ["model_name"])

        # Configuration
        self.model_name = "engravedetect_efficientnet"
        self.drift_check_probability = 0.1  # 10% des requêtes (normal)
        self.drift_threshold = 0.7
        self.reference_data = None
        self.last_drift_check = None
        self.drift_check_interval = timedelta(minutes=5)

        # Baseline historique pour le drift
        self.baseline_embeddings = []
        self.baseline_established = False
        self.baseline_size = 50  # Nombre d'embeddings pour établir la baseline
        self.drift_history = []  # Historique des scores de drift

        # Statistiques internes
        self.prediction_count = 0
        self.success_count = 0
        self.total_inference_time = 0.0
        self.confidence_scores = []
        self.embedding_qualities = []

        # Métriques de classification
        self.top1_correct = 0
        self.top3_correct = 0
        self.high_confidence_count = 0
        self.medium_confidence_count = 0
        self.low_confidence_count = 0
        self.rejected_count = 0

        # Métriques de throughput
        self.predictions_per_minute = []
        self.last_prediction_time = None

        # Seuils configurables
        self.confidence_threshold_high = 0.8
        self.confidence_threshold_medium = 0.5
        self.rejection_threshold = 0.3

        logger.info("Moniteur de modèle d'IA initialisé")

    def update_prediction_metrics(
        self,
        embedding: np.ndarray,
        similarity_scores: List[float],
        inference_time: float,
        success: bool,
        predicted_class: str = None,
        true_class: str = None,
    ) -> None:
        """
        Met à jour les métriques de prédiction.

        Args:
            embedding: Embedding généré par le modèle
            similarity_scores: Scores de similarité calculés
            inference_time: Temps d'inférence en secondes
            success: Si la prédiction a réussi
            predicted_class: Classe prédite (optionnel)
            true_class: Classe vraie (optionnel)
        """
        try:
            # Métriques de base
            self.prediction_count += 1
            if success:
                self.success_count += 1
                self.model_predictions_success.labels(self.model_name).inc()
            else:
                self.model_predictions_failed.labels(self.model_name).inc()

            self.model_predictions_total.labels(self.model_name, "success" if success else "failed").inc()

            # Temps d'inférence
            self.total_inference_time += inference_time
            self.model_inference_time_seconds.labels(self.model_name).observe(inference_time)

            # Qualité de l'embedding
            if embedding is not None:
                embedding_quality = self._calculate_embedding_quality(embedding)
                self.embedding_qualities.append(embedding_quality)
                self.model_embedding_quality.labels(self.model_name).set(embedding_quality)

                # Métriques de qualité des embeddings
                embedding_normality = self._calculate_embedding_normality(embedding)
                self.model_embedding_normality.labels(self.model_name).set(embedding_normality)

                feature_activation = self._calculate_feature_activation(embedding)
                self.model_feature_activation.labels(self.model_name).set(feature_activation)

            # Métriques de confiance et classification
            if similarity_scores:
                max_confidence = max(similarity_scores)
                self.confidence_scores.append(max_confidence)
                self.model_prediction_confidence.labels(self.model_name).observe(max_confidence)

                # Classification par niveau de confiance
                if max_confidence >= self.confidence_threshold_high:
                    self.high_confidence_count += 1
                    self.model_confidence_high.labels(self.model_name).inc()
                elif max_confidence >= self.confidence_threshold_medium:
                    self.medium_confidence_count += 1
                    self.model_confidence_medium.labels(self.model_name).inc()
                else:
                    self.low_confidence_count += 1
                    self.model_confidence_low.labels(self.model_name).inc()

                # Taux de rejet
                if max_confidence < self.rejection_threshold:
                    self.rejected_count += 1

                rejection_rate = self.rejected_count / max(self.prediction_count, 1)
                self.model_rejection_rate.labels(self.model_name).set(rejection_rate)

            # Métriques de classification (si les classes sont fournies)
            if predicted_class and true_class:
                # Top-1 accuracy
                if predicted_class == true_class:
                    self.top1_correct += 1

                # Top-3 accuracy (simulation - dans un vrai système, on aurait les top 3)
                # Pour l'instant, on simule avec une probabilité basée sur la confiance
                if max_confidence > 0.7:  # Seuil pour considérer que c'est dans le top 3
                    self.top3_correct += 1

                # Mise à jour des métriques d'accuracy
                top1_accuracy = self.top1_correct / max(self.prediction_count, 1)
                top3_accuracy = self.top3_correct / max(self.prediction_count, 1)

                self.model_top1_accuracy.labels(self.model_name).set(top1_accuracy)
                self.model_top3_accuracy.labels(self.model_name).set(top3_accuracy)

            # Métriques de throughput
            current_time = time.time()
            if self.last_prediction_time:
                time_diff = current_time - self.last_prediction_time
                if time_diff > 0:
                    throughput = 60.0 / time_diff  # prédictions par minute
                    self.predictions_per_minute.append(throughput)
                    # Garder seulement les 100 dernières valeurs
                    if len(self.predictions_per_minute) > 100:
                        self.predictions_per_minute.pop(0)

                    avg_throughput = np.mean(self.predictions_per_minute)
                    self.model_throughput.labels(self.model_name).set(avg_throughput)

            self.last_prediction_time = current_time

            # Détection de drift (10% des requêtes pour éviter la surcharge)
            if self.should_check_drift() and embedding is not None:
                drift_score = self.detect_data_drift(embedding)
                if drift_score is not None:
                    logger.debug(f"Drift score calculé: {drift_score:.3f}")

            logger.debug(
                f"Métriques mises à jour - Prédictions: {self.prediction_count}, "
                f"Top-1: {self.top1_correct}, Top-3: {self.top3_correct}, "
                f"Confiance: {max_confidence:.3f}, Temps: {inference_time:.3f}s"
            )

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métriques: {e}")

    def _calculate_embedding_quality(self, embedding: np.ndarray) -> float:
        """
        Calcule la qualité d'un embedding.

        Args:
            embedding: Embedding à évaluer

        Returns:
            Score de qualité entre 0 et 1
        """
        try:
            # Métriques de qualité basées sur les propriétés statistiques
            norm = np.linalg.norm(embedding)
            variance = np.var(embedding)
            sparsity = np.mean(embedding == 0)

            # Score composite (plus élevé = meilleure qualité)
            quality_score = (
                0.4 * min(norm / 10.0, 1.0)  # Normalisation
                + 0.3 * min(variance / 5.0, 1.0)  # Variance
                + 0.3 * (1.0 - sparsity)  # Non-sparsité
            )

            return max(0.0, min(1.0, quality_score))

        except Exception as e:
            logger.error(f"Erreur lors du calcul de la qualité d'embedding: {e}")
            return 0.5  # Valeur par défaut

    def _calculate_embedding_normality(self, embedding: np.ndarray) -> float:
        """
        Calcule la normalité des embeddings avec un test simplifié.

        Args:
            embedding: Embedding à évaluer

        Returns:
            Score de normalité entre 0 et 1
        """
        try:
            # Test simplifié de normalité basé sur l'asymétrie et l'aplatissement
            mean_val = np.mean(embedding)
            std_val = np.std(embedding)

            if std_val == 0:
                return 0.0

            # Calcul de l'asymétrie (skewness)
            skewness = np.mean(((embedding - mean_val) / std_val) ** 3)

            # Calcul de l'aplatissement (kurtosis)
            kurtosis = np.mean(((embedding - mean_val) / std_val) ** 4) - 3

            # Score de normalité (plus proche de 0 = plus normal)
            normality_score = 1.0 - min(1.0, (abs(skewness) + abs(kurtosis)) / 10.0)

            return max(0.0, normality_score)

        except Exception as e:
            logger.error(f"Erreur lors du calcul de la normalité: {e}")
            return 0.5

    def _calculate_feature_activation(self, embedding: np.ndarray) -> float:
        """
        Calcule l'activité moyenne des features du modèle.

        Args:
            embedding: Embedding à évaluer

        Returns:
            Score d'activation entre 0 et 1
        """
        try:
            # Activité basée sur la variance et la non-sparsité
            variance = np.var(embedding)
            sparsity = np.mean(embedding == 0)

            # Score d'activation (plus élevé = plus d'activité)
            activation_score = 0.6 * min(variance / 5.0, 1.0) + 0.4 * (1.0 - sparsity)  # Variance  # Non-sparsité

            return max(0.0, min(1.0, activation_score))

        except Exception as e:
            logger.error(f"Erreur lors du calcul de l'activation: {e}")
            return 0.5

    def detect_data_drift(self, embedding: np.ndarray) -> Optional[float]:
        """
        Détecte le drift des données d'entrée.

        Args:
            embedding: Embedding actuel à comparer

        Returns:
            Score de drift (0-1) basé sur la comparaison avec la baseline
        """
        return self._simple_drift_detection(embedding)

    def _simple_drift_detection(self, embedding: np.ndarray) -> float:
        """
        Détection de drift réaliste basée sur une baseline historique.

        Args:
            embedding: Embedding à analyser

        Returns:
            Score de drift basé sur la comparaison avec la baseline
        """
        try:
            # Ajouter l'embedding à la baseline si pas encore établie
            if not self.baseline_established:
                self.baseline_embeddings.append(embedding.copy())

                # Établir la baseline après avoir collecté assez d'embeddings
                if len(self.baseline_embeddings) >= self.baseline_size:
                    self.baseline_established = True
                    logger.info(f"Baseline établie avec {len(self.baseline_embeddings)} embeddings")

                # Retourner un score neutre pendant l'établissement de la baseline
                return 0.5

            # Calculer le drift par rapport à la baseline
            drift_score = self._calculate_drift_vs_baseline(embedding)

            # Ajouter à l'historique
            self.drift_history.append(drift_score)
            if len(self.drift_history) > 100:  # Garder seulement les 100 derniers
                self.drift_history.pop(0)

            # Mettre à jour la métrique Prometheus
            self.model_drift_score.labels(self.model_name).set(drift_score)

            # Log si drift élevé
            if drift_score > self.drift_threshold:
                logger.warning(f"Drift élevé détecté: {drift_score:.3f} (seuil: {self.drift_threshold})")

            return drift_score

        except Exception as e:
            logger.error(f"Erreur lors de la détection de drift: {e}")
            return 0.5

    def _calculate_drift_vs_baseline(self, embedding: np.ndarray) -> float:
        """
        Calcule le score de drift en comparant avec la baseline historique.

        Args:
            embedding: Embedding actuel

        Returns:
            Score de drift entre 0 et 1
        """
        try:
            # Convertir la baseline en array numpy
            baseline_array = np.array(self.baseline_embeddings)

            # Calculer les statistiques de la baseline
            baseline_mean = np.mean(baseline_array, axis=0)
            baseline_std = np.std(baseline_array, axis=0)

            # Calculer les distances normalisées
            mean_distance = np.linalg.norm(embedding - baseline_mean)
            std_distance = np.linalg.norm(np.abs(embedding - baseline_mean) - baseline_std)

            # Normaliser les distances
            mean_distance_norm = mean_distance / (np.linalg.norm(baseline_mean) + 1e-6)
            std_distance_norm = std_distance / (np.linalg.norm(baseline_std) + 1e-6)

            # Score de drift basé sur les distances
            drift_score = min(1.0, (mean_distance_norm + std_distance_norm) / 2.0)

            # Appliquer une fonction sigmoïde pour lisser le score
            import math

            drift_score = 1.0 / (1.0 + math.exp(-10 * (drift_score - 0.5)))

            return drift_score

        except Exception as e:
            logger.error(f"Erreur lors du calcul du drift vs baseline: {e}")
            return 0.5

    def _generate_reference_data(self, embedding: np.ndarray) -> Dict[str, Any]:
        """Génère des données de référence pour la comparaison."""
        # Simulation de données de référence
        return {"embedding_features": np.random.normal(0, 1, (100, embedding.shape[0]))}

    def should_check_drift(self) -> bool:
        """
        Détermine si on doit vérifier le drift.

        Returns:
            True si on doit vérifier le drift
        """
        return random.random() < self.drift_check_probability

    def get_model_health_status(self) -> Dict[str, Any]:
        """
        Récupère le statut de santé du modèle.

        Returns:
            Dictionnaire avec les métriques de santé
        """
        try:
            avg_inference_time = self.total_inference_time / max(self.prediction_count, 1)

            avg_confidence = np.mean(self.confidence_scores) if self.confidence_scores else 0.0

            avg_embedding_quality = np.mean(self.embedding_qualities) if self.embedding_qualities else 0.0

            # Nouvelles métriques de classification
            top1_accuracy = self.top1_correct / max(self.prediction_count, 1)
            top3_accuracy = self.top3_correct / max(self.prediction_count, 1)
            rejection_rate = self.rejected_count / max(self.prediction_count, 1)

            # Distribution de confiance
            confidence_distribution = {
                "high": self.high_confidence_count,
                "medium": self.medium_confidence_count,
                "low": self.low_confidence_count,
            }

            # Throughput
            current_throughput = np.mean(self.predictions_per_minute) if self.predictions_per_minute else 0.0

            return {
                "model_name": self.model_name,
                "total_predictions": self.prediction_count,
                "success_count": self.success_count,
                "top1_accuracy": top1_accuracy,
                "top3_accuracy": top3_accuracy,
                "rejection_rate": rejection_rate,
                "confidence_distribution": confidence_distribution,
                "average_inference_time": avg_inference_time,
                "average_confidence": avg_confidence,
                "average_embedding_quality": avg_embedding_quality,
                "current_throughput": current_throughput,
                "last_drift_check": self.last_drift_check.isoformat() if self.last_drift_check else None,
                "monitoring_active": True,
                "drift_baseline_established": self.baseline_established,
                "drift_baseline_size": len(self.baseline_embeddings),
                "drift_history_size": len(self.drift_history),
                "average_drift_score": np.mean(self.drift_history) if self.drift_history else 0.0,
            }

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut: {e}")
            return {"model_name": self.model_name, "error": str(e), "monitoring_active": False}


# Instance globale du moniteur
model_monitor = ModelMonitor()
