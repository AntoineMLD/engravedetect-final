"""
Collecteur de métriques pour le monitoring de l'API.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..core.config import REPORTS_DIR

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collecte et stocke les métriques de l'API.
    """

    def __init__(self):
        self.temp_predictions: List[Dict[str, Any]] = []
        self.validated_predictions: List[Dict[str, Any]] = []

    def add_temp_prediction(self, prediction: Dict[str, Any]) -> None:
        """
        Ajoute une prédiction temporaire.
        """
        self.temp_predictions.append(prediction)
        if len(self.temp_predictions) > 100:  # Garder seulement les 100 dernières prédictions
            self.temp_predictions.pop(0)

    def validate_last_prediction(self, true_label: str) -> bool:
        """
        Valide la dernière prédiction.
        """
        if not self.temp_predictions:
            return False

        prediction = self.temp_predictions.pop()
        prediction["true_label"] = true_label
        prediction["validated_at"] = datetime.now()
        self.validated_predictions.append(prediction)

        # Sauvegarder après chaque validation
        self._save_predictions()
        return True

    def generate_report(self) -> Optional[Dict[str, Any]]:
        """
        Génère un rapport des métriques.
        """
        if not self.validated_predictions:
            return None

        total = len(self.validated_predictions)
        correct = sum(1 for p in self.validated_predictions if p["predicted_label"] == p["true_label"])

        avg_confidence = sum(p["confidence"] for p in self.validated_predictions) / total
        avg_time = sum(p["processing_time"] for p in self.validated_predictions) / total

        return {
            "n_predictions": total,
            "accuracy": correct / total,
            "avg_confidence": avg_confidence,
            "avg_processing_time": avg_time,
        }

    def _save_predictions(self) -> None:
        """
        Sauvegarde les prédictions validées.
        """
        try:
            filename = os.path.join(REPORTS_DIR, "validated_predictions.json")
            with open(filename, "w") as f:
                json.dump(self.validated_predictions, f, default=str)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des prédictions: {e}")


# Instance globale du collecteur de métriques
monitor = MetricsCollector()
