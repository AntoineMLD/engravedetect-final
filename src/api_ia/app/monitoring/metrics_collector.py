"""
Collecteur de métriques en temps réel pour le monitoring de performance du modèle d'IA.

Ce module définit la classe ModelMonitor, un singleton responsable de :
- L'enregistrement des prédictions temporaires du modèle.
- La validation de ces prédictions (par exemple, par une intervention humaine).
- Le stockage persistant des prédictions validées.
- Le calcul et la génération de rapports de métriques de performance
  basées sur les prédictions validées.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
from collections import deque
import logging
from functools import lru_cache
from ..config import REPORTS_DIR

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ModelMonitor:
    """
    Singleton pour le monitoring des performances du modèle d'IA.

    Gère une fenêtre glissante de prédictions validées pour calculer des métriques
    pertinentes telles que la confiance moyenne, le temps de traitement moyen,
    la distribution des classes et la précision (si la validation humaine est fournie).
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("Nouvelle instance de ModelMonitor créée")
        return cls._instance

    def __init__(self, window_size=1000):
        """
        Initialise le moniteur de modèle.

        Args:
            window_size (int): Taille de la fenêtre glissante pour stocker
                              les prédictions validées et calculer les métriques.
        """
        # Éviter la réinitialisation si déjà initialisé
        if hasattr(self, "initialized"):
            return

        self.initialized = True
        self.window_size = window_size
        # Stocke les prédictions après validation par l'utilisateur
        self.validated_predictions = deque(maxlen=window_size)
        # Stocke les prédictions brutes du modèle avant validation
        self.temp_predictions = deque(maxlen=10)
        # DataFrame Pandas contenant les données des prédictions validées pour calculs
        self.current_data = None

        # Configuration des chemins
        self.reports_dir = REPORTS_DIR
        self.history_file = os.path.join(self.reports_dir, "predictions_history.json")
        os.makedirs(self.reports_dir, exist_ok=True)
        logger.info(f"Utilisation du dossier des rapports: {self.reports_dir}")

        # Charger l'historique des prédictions
        self._load_history()

    def _validate_prediction_data(self, pred):
        """Valide la structure et les types des données de prédiction."""
        required_fields = ["timestamp", "predicted_label", "confidence", "processing_time"]

        # Vérifier les champs requis
        for field in required_fields:
            if field not in pred:
                logger.warning(f"Champ manquant dans la prédiction : {field}")
                return None

        # S'assurer que le timestamp est une chaîne ISO
        if isinstance(pred["timestamp"], datetime):
            pred["timestamp"] = pred["timestamp"].isoformat()

        # Convertir les valeurs numériques si nécessaire
        try:
            pred["confidence"] = float(pred["confidence"])
            pred["processing_time"] = float(pred["processing_time"])
        except (ValueError, TypeError):
            logger.warning("Erreur de conversion des valeurs numériques")
            return None

        return pred

    def _load_history(self):
        """Charge l'historique des prédictions validées depuis le fichier JSON."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    history = json.load(f)

                if isinstance(history, list):
                    # Valider et ajouter chaque prédiction de l'historique
                    for pred in history:
                        validated_pred = self._validate_prediction_data(pred)
                        if validated_pred:
                            self.validated_predictions.append(validated_pred)

                    # Mettre à jour le DataFrame pour les calculs
                    self._update_dataframe()
                    logger.info(f"Historique chargé avec {len(self.validated_predictions)} prédictions")
                else:
                    logger.warning("Format d'historique invalide. Attendu: liste")
            else:
                logger.info("Aucun fichier d'historique trouvé. Création d'un nouvel historique.")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'historique: {str(e)}")

    def _save_history(self):
        """Sauvegarde l'historique des prédictions validées dans un fichier JSON."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(list(self.validated_predictions), f)
            logger.info(f"Historique sauvegardé avec {len(self.validated_predictions)} prédictions")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'historique: {str(e)}")

    def _update_dataframe(self):
        """Met à jour le DataFrame interne avec les prédictions validées pour les calculs."""
        if self.validated_predictions:
            self.current_data = pd.DataFrame(self.validated_predictions)
            logger.debug(f"DataFrame mis à jour avec {len(self.current_data)} prédictions")
        else:
            self.current_data = None
            logger.debug("DataFrame réinitialisé (aucune prédiction validée)")

    def add_temp_prediction(self, prediction):
        """
        Ajoute une prédiction temporaire du modèle (non validée par l'utilisateur).

        Args:
            prediction (dict): Dictionnaire contenant les données de prédiction.
                Doit contenir au minimum:
                - timestamp
                - predicted_label
                - confidence
                - processing_time
        """
        validated = self._validate_prediction_data(prediction)
        if validated:
            # Stocker la prédiction dans la liste temporaire
            if "original_prediction" not in validated:
                validated["original_prediction"] = validated["predicted_label"]
            self.temp_predictions.append(validated)
            logger.info(f"Prédiction temporaire ajoutée pour la classe: {validated['predicted_label']}")
        else:
            logger.warning("Prédiction temporaire invalide. Non ajoutée.")

    def validate_last_prediction(self, validated_label):
        """
        Valide la dernière prédiction temporaire avec le label confirmé par l'utilisateur.

        Args:
            validated_label (str): Label de classe validé par l'utilisateur.
        """
        if not self.temp_predictions:
            logger.warning("Aucune prédiction temporaire à valider")
            return False

        # Prendre la dernière prédiction temporaire
        last_pred = self.temp_predictions.pop()

        # Stocker le label original si différent du label validé
        if "original_prediction" not in last_pred:
            last_pred["original_prediction"] = last_pred["predicted_label"]

        # Mettre à jour avec le label validé
        last_pred["predicted_label"] = validated_label

        # Ajouter aux prédictions validées
        self.validated_predictions.append(last_pred)

        # Mettre à jour le DataFrame et sauvegarder l'historique
        self._update_dataframe()
        self._save_history()

        logger.info(f"Prédiction validée avec le label: {validated_label}")
        return True

    def generate_report(self):
        """
        Génère un rapport contenant un ensemble de métriques de performance du modèle,
        calculées sur la fenêtre actuelle de prédictions validées.

        Le rapport est également sauvegardé en JSON dans le dossier 'reports'.

        Les métriques incluses sont :
        - timestamp: Date et heure de génération du rapport.
        - avg_confidence: Confiance moyenne des prédictions originales du modèle
                          pour les cas qui ont été validés.
        - avg_processing_time: Temps de traitement moyen par prédiction.
        - n_predictions: Nombre total de prédictions validées dans la fenêtre actuelle.
        - predictions_per_class: Distribution des labels de classe validés.
        - prediction_accuracy: Précision du modèle, calculée en comparant la prédiction
                              originale du modèle au label validé par l'utilisateur.
                              (label validé est considéré comme la vérité terrain).

        Returns:
            dict or None: Un dictionnaire contenant les métriques, ou None si
                          aucune donnée de prédiction validée n'est disponible.
        """
        if self.current_data is None or len(self.current_data) < 1:
            logger.warning("Aucune donnée de prédiction validée disponible pour générer un rapport.")
            return None

        metrics = {
            # Timestamp de la génération de ce rapport
            "timestamp": datetime.now().isoformat(),
            # Confiance moyenne des prédictions originales du modèle
            "avg_confidence": self._calculate_avg_confidence(),
            # Temps de traitement moyen pour une prédiction par le modèle
            "avg_processing_time": self._calculate_avg_processing_time(),
            # Nombre total de prédictions validées utilisées pour ce rapport
            "n_predictions": len(self.current_data),
            # Distribution des classes (labels validés)
            "predictions_per_class": self._count_predictions_per_class(),
            # Précision du modèle basée sur la validation utilisateur
            "prediction_accuracy": self._calculate_prediction_accuracy(),
        }

        metrics_path = os.path.join(self.reports_dir, f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(metrics_path, "w") as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"Rapport de métriques sauvegardé dans {metrics_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du rapport de métriques : {e}")

        return metrics

    def _calculate_avg_confidence(self):
        """
        Calcule la confiance moyenne des prédictions originales du modèle
        sur la fenêtre courante de prédictions validées.
        La confiance est celle initialement retournée par le modèle, même si le label
        a été corrigé lors de la validation.
        """
        if self.current_data is None or "confidence" not in self.current_data.columns or self.current_data["confidence"].empty:
            return 0.0
        return float(self.current_data["confidence"].mean())

    def _calculate_avg_processing_time(self):
        """
        Calcule le temps de traitement moyen des prédictions
        sur la fenêtre courante de prédictions validées.
        """
        if (
            self.current_data is None
            or "processing_time" not in self.current_data.columns
            or self.current_data["processing_time"].empty
        ):
            return 0.0
        return float(self.current_data["processing_time"].mean())

    def _count_predictions_per_class(self):
        """
        Compte le nombre de prédictions validées pour chaque classe (label validé)
        sur la fenêtre courante. Utile pour voir la distribution des labels
        confirmés par l'utilisateur.
        """
        if (
            self.current_data is None
            or "predicted_label" not in self.current_data.columns
            or self.current_data["predicted_label"].empty
        ):
            return {}
        return self.current_data["predicted_label"].value_counts().to_dict()

    def _calculate_prediction_accuracy(self):
        """
        Calcule la précision des prédictions du modèle sur la fenêtre courante.
        La précision est définie comme le pourcentage de prédictions où le label
        prédit originalement par le modèle ('original_prediction') correspond au
        label validé par l'utilisateur ('predicted_label').
        Nécessite que 'original_prediction' et 'predicted_label' soient présents.
        """
        if (
            self.current_data is None
            or "original_prediction" not in self.current_data.columns
            or "predicted_label" not in self.current_data.columns
        ):
            logger.warning(
                "Données insuffisantes pour calculer la précision (original_prediction ou predicted_label manquant)."
            )
            return 0.0

        correct_predictions = (self.current_data["original_prediction"] == self.current_data["predicted_label"]).sum()
        total_predictions = len(self.current_data)

        if total_predictions == 0:
            return 0.0

        return float(correct_predictions / total_predictions)


# Instance globale du moniteur
monitor = ModelMonitor()
