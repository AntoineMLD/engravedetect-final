"""
Monitoring du modèle IA EngraveDetect.
Expose des métriques Prometheus pertinentes et réalistes pour la prod.
"""

import logging
from typing import Dict, List, Optional

import numpy as np
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class ModelMonitor:
    """
    Moniteur centralisé pour les métriques du modèle IA.
    """

    def __init__(self, model_name: str = "engravedetect_efficientnet"):
        self.model_name = model_name

        # ----- Compteurs généraux -----
        self.predictions_total = Counter(
            "model_predictions_total",
            "Nombre total de prédictions",
            ["model_name", "status"],  # success/failed
        )

        self.predicted_classes = Counter(
            "model_predicted_classes_total",
            "Distribution des classes prédites",
            ["model_name", "class"],
        )

        # ----- Accuracy (via vérité connue) -----
        self.topk_predictions = Counter(
            "model_accuracy_predictions_total",
            "Nombre de prédictions évaluées pour Top-k",
            ["model_name", "k"],  # "1", "3", ...
        )
        self.topk_correct = Counter(
            "model_accuracy_correct_total",
            "Nombre de prédictions correctes pour Top-k",
            ["model_name", "k"],
        )

        # ----- Confiance / ambiguïté -----
        self.confidence = Histogram(
            "model_prediction_confidence",
            "Confiance top-1",
            ["model_name"],
            buckets=[i / 10 for i in range(11)],  # 0.0 .. 1.0
        )

        self.top1_margin = Histogram(
            "model_prediction_top1_margin",
            "Écart de similarité entre top-1 et top-2",
            ["model_name"],
            buckets=[i / 100 for i in range(0, 51, 5)],  # 0.00 .. 0.50
        )

        self.ambiguous_predictions = Counter(
            "model_ambiguous_predictions_total",
            "Prédictions ambiguës (margin < seuil)",
            ["model_name", "threshold"],  # ex: "0.05"
        )

        # ----- Latence -----
        self.inference_latency = Histogram(
            "model_inference_latency_seconds",
            "Temps d'inférence (s)",
            ["model_name"],
            buckets=[0.05, 0.1, 0.2, 0.5, 1, 2, 5],
        )

        # ----- Drift -----
        self.drift_score = Gauge(
            "model_drift_score",
            "Score de drift (0=OK, 1=max)",
            ["model_name"],
        )
        self.drift_status = Gauge(
            "model_drift_status",
            "Statut drift: 0=OK,1=warn,2=alert",
            ["model_name"],
        )

        # ----- “Dernière valeur” pour affichage lisible -----
        self.last_predicted_class = Gauge(
            "model_last_predicted_class",
            "Dernière classe top-1 prédite (1 pour la classe courante)",
            ["model_name", "class"],
        )
        self.user_last_expected_tag = Gauge(
            "user_last_expected_tag",
            "Dernier tag attendu côté utilisateur (1 pour le tag courant)",
            ["model_name", "tag"],
        )
        self._prev_predicted_class: Optional[str] = None
        self._prev_expected_tag: Optional[str] = None

        # ----- Inputs (diagnostic) -----
        self.input_brightness = Histogram(
            "model_input_brightness",
            "Luminosité moyenne des images (0-1)",
            ["model_name"],
            buckets=[i / 20 for i in range(21)],  # 0.00 .. 1.00
        )
        self.input_width = Histogram(
            "model_input_width_px",
            "Largeur des images (px)",
            ["model_name"],
            buckets=[64, 128, 224, 320, 480, 640, 800, 1024, 1280, 1600, 1920],
        )
        self.input_height = Histogram(
            "model_input_height_px",
            "Hauteur des images (px)",
            ["model_name"],
            buckets=[64, 128, 224, 320, 480, 640, 800, 1024, 1280, 1600, 1920],
        )
        self.payload_size = Histogram(
            "model_request_payload_bytes",
            "Taille des fichiers uploadés (octets)",
            ["model_name"],
            buckets=[1 << i for i in range(10, 22)],  # 1KB .. 4MB
        )

    # ------------------------------------------------------------------
    # Updates
    # ------------------------------------------------------------------

    def observe_prediction(
        self,
        embedding: Optional[np.ndarray],
        similarity_scores: List[float],
        inference_time: float,
        success: bool,
        predicted_class: str,
        true_class: Optional[str] = None,
        topk_classes: Optional[List[str]] = None,
        image_info: Optional[Dict] = None,
    ) -> None:
        """
        Met à jour les métriques liées à une prédiction unique.
        - topk_classes: liste ordonnée des classes (top-1, top-2, …) si disponible.
        """
        try:
            status = "success" if success else "failed"
            self.predictions_total.labels(self.model_name, status).inc()

            # Latence
            self.inference_latency.labels(self.model_name).observe(float(inference_time))

            if not success or not similarity_scores:
                return

            # Confiance top-1
            top1_conf = float(similarity_scores[0])
            self.confidence.labels(self.model_name).observe(top1_conf)

            # Ambiguïté = écart top1-top2
            if len(similarity_scores) > 1:
                margin = float(similarity_scores[0] - similarity_scores[1])
                self.top1_margin.labels(self.model_name).observe(margin)
                if margin < 0.05:
                    self.ambiguous_predictions.labels(self.model_name, "0.05").inc()

            # Distribution des classes prédites
            if predicted_class:
                self.predicted_classes.labels(self.model_name, predicted_class).inc()

            # Accuracy (si vérité fournie)
            if true_class:
                # Top-1
                self.topk_predictions.labels(self.model_name, "1").inc()
                if predicted_class == true_class:
                    self.topk_correct.labels(self.model_name, "1").inc()

                # Top-3 : seulement si on reçoit la liste des classes
                self.topk_predictions.labels(self.model_name, "3").inc()
                if topk_classes and true_class in topk_classes[:3]:
                    self.topk_correct.labels(self.model_name, "3").inc()

            # Inputs (diagnostic)
            if image_info:
                b = image_info.get("brightness")
                w = image_info.get("width")
                h = image_info.get("height")
                p = image_info.get("payload_size")
                if b is not None:
                    self.input_brightness.labels(self.model_name).observe(float(b))
                if w is not None:
                    self.input_width.labels(self.model_name).observe(float(w))
                if h is not None:
                    self.input_height.labels(self.model_name).observe(float(h))
                if p is not None:
                    self.payload_size.labels(self.model_name).observe(float(p))

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métriques: {e}")

    # ---------------- Dernière valeur (panneaux lisibles) ----------------

    def set_last_predicted_class(self, predicted_class: Optional[str]) -> None:
        try:
            if self._prev_predicted_class is not None:
                self.last_predicted_class.labels(self.model_name, self._prev_predicted_class).set(0)
            if predicted_class:
                self.last_predicted_class.labels(self.model_name, predicted_class).set(1)
                self._prev_predicted_class = predicted_class
        except Exception as e:
            logger.error(f"set_last_predicted_class error: {e}")

    def set_last_expected_tag(self, tag: Optional[str]) -> None:
        try:
            if self._prev_expected_tag is not None:
                self.user_last_expected_tag.labels(self.model_name, self._prev_expected_tag).set(0)
            if tag:
                self.user_last_expected_tag.labels(self.model_name, tag).set(1)
                self._prev_expected_tag = tag
        except Exception as e:
            logger.error(f"set_last_expected_tag error: {e}")

    # ------------------------------ Drift -------------------------------

    def update_drift(self, score: float) -> None:
        try:
            score = float(score)
            self.drift_score.labels(self.model_name).set(score)
            if score < 0.3:
                self.drift_status.labels(self.model_name).set(0)
            elif score < 0.6:
                self.drift_status.labels(self.model_name).set(1)
            else:
                self.drift_status.labels(self.model_name).set(2)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du drift: {e}")

    # ------------------------------ Health ------------------------------

    def get_model_health_status(self) -> dict:
        return {"model_name": self.model_name, "monitoring_active": True}


# Instance globale
model_monitor = ModelMonitor()
