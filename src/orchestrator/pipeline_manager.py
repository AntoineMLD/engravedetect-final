"""
Module d'orchestration du pipeline de données optiques.

Ce module contient la classe DataPipelineManager qui orchestre l'ensemble
du pipeline de traitement des données optiques, du scraping à la création
des tables finales en base de données.

Fonctionnalités :
- Configuration automatique du logging et des chemins
- Chargement dynamique des spiders Scrapy
- Exécution séquentielle des étapes du pipeline
- Gestion des erreurs et monitoring des processus
- Export des données vers PostgreSQL

Pipeline complet :
1. Exécution des spiders de scraping
2. Export des données brutes vers staging
3. Nettoyage et enrichissement des données
4. Export des données finales vers verres

Auteur : Équipe de développement
Version : 1.0.0
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import scrapy
import sys
from ..database.reset_database import reset_database


class DataPipelineManager:
    """
    Orchestrateur principal du pipeline de données optiques.

    Cette classe gère l'ensemble du flux de données, du scraping à la création des tables finales.
    Elle encapsule toutes les étapes du pipeline, la configuration du logging, le chargement des dépendances,
    et fournit des méthodes pour exécuter chaque étape ou le pipeline complet.

    Exemple d'utilisation :
        pipeline = DataPipelineManager()
        pipeline.run_full_pipeline()
    """

    def __init__(self):
        """
        Initialise le pipeline, configure le logging, les chemins et charge les dépendances.
        """
        self._setup_logging()
        self._setup_paths()
        self._load_dependencies()

    def _setup_logging(self) -> None:
        """
        Configure le système de logging pour le pipeline.
        Crée un fichier de log daté et configure la sortie console.
        """
        log_format = "%(asctime)s [%(levelname)s] %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        # Créer le dossier logs s'il n'existe pas
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Configurer le fichier de log avec la date
        log_file = logs_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        self.logger = logging.getLogger(__name__)

    def _setup_paths(self) -> None:
        """
        Configure les chemins du projet et ajoute le projet au PYTHONPATH pour Scrapy.
        """
        # Obtenir le chemin absolu du projet
        self.project_root = Path(__file__).resolve().parents[2]

        # Ajouter le chemin du projet au PYTHONPATH pour que Scrapy trouve les settings
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
            self.logger.info(f"Ajout du chemin du projet au PYTHONPATH: {self.project_root}")

    def _load_dependencies(self) -> None:
        """
        Charge dynamiquement les spiders Scrapy et le nettoyeur de données.
        """
        try:
            from src.data.scraping.france_optique.spiders import (
                glass_spider,
                glass_spider_hoya,
                glass_spider_full_xpath,
                glass_spider_particular,
                glass_spider_optovision,
                glass_spider_indo_optical,
            )
            from src.data.processing.cleaner import OpticalDataCleaner

            self.spiders = {
                "base": glass_spider,
                "hoya": glass_spider_hoya,
                "full_xpath": glass_spider_full_xpath,
                "particular": glass_spider_particular,
                "optovision": glass_spider_optovision,
                "indo_optical": glass_spider_indo_optical,
            }

            self.cleaner = OpticalDataCleaner()
            self.logger.info("Dépendances chargées avec succès")

        except ImportError as e:
            self.logger.error(f" Erreur lors du chargement des dépendances : {e}")
            raise

    def run_spiders(self) -> bool:
        """
        Lance tous les spiders Scrapy pour collecter les données brutes.

        Returns:
            bool: True si tous les spiders ont réussi, False sinon.

        Exemple d'utilisation :
            pipeline = DataPipelineManager()
            pipeline.run_spiders()
        """
        self.logger.info("Démarrage des spiders...")

        try:
            from scrapy.crawler import CrawlerProcess
            from scrapy.utils.project import get_project_settings

            process = CrawlerProcess(get_project_settings())

            # Ajouter chaque spider au processus
            for spider_name, spider_module in self.spiders.items():
                self.logger.info(f" Ajout du spider {spider_name}")
                # Obtenir la classe Spider directement du module
                spider_class = next(
                    obj
                    for name, obj in spider_module.__dict__.items()
                    if isinstance(obj, type) and issubclass(obj, scrapy.Spider)
                )
                process.crawl(spider_class)

            # Lancer tous les spiders
            process.start()

            self.logger.info("Tous les spiders ont terminé avec succès")
            return True

        except Exception as e:
            self.logger.error(f" Erreur lors de l'exécution des spiders : {e}")
            return False

    def export_staging_data(self) -> Optional[str]:
        """
        Exporte les données de la table staging en CSV via le cleaner.

        Returns:
            Optional[str]: Chemin du fichier CSV généré ou None en cas d'erreur.
        """
        self.logger.info("Export des données staging en CSV...")
        try:
            # Charger les données de staging
            df = self.cleaner.load_data_from_staging()
            if df.empty:
                self.logger.warning(" Aucune donnée trouvée dans la table staging")
                return None

            # Exporter en CSV
            csv_path = self.cleaner.export_to_csv(df)
            self.logger.info(f"Données staging exportées vers {csv_path}")
            return csv_path
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export staging : {e}")
            return None

    def clean_and_enhance_data(self) -> bool:
        """
        Nettoie les données brutes et les insère dans la table enhanced.

        Returns:
            bool: True si le processus a réussi, False sinon.
        """
        self.logger.info("🧹 Nettoyage et amélioration des données...")
        try:
            # Charger et nettoyer les données
            df_raw = self.cleaner.load_data_from_staging()
            if df_raw.empty:
                self.logger.error("Aucune donnée à nettoyer dans la table staging")
                return False

            df_clean = self.cleaner.clean_dataframe(df_raw)
            if df_clean.empty:
                self.logger.error("Aucune donnée valide après nettoyage")
                return False

            # Créer la table enhanced et insérer les données
            self.cleaner.create_enhanced_table()
            self.cleaner.insert_to_enhanced(df_clean)

            # Afficher les statistiques
            self.cleaner.get_data_statistics(df_clean)

            self.logger.info("Données nettoyées et améliorées avec succès")
            return True
        except Exception as e:
            self.logger.error(f" Erreur lors du nettoyage des données : {e}")
            return False

    def export_enhanced_data(self) -> Optional[str]:
        """
        Exporte les données de la table enhanced en CSV via le cleaner.

        Returns:
            Optional[str]: Chemin du fichier CSV généré ou None en cas d'erreur.
        """
        self.logger.info("Export des données enhanced en CSV...")
        try:
            # Charger les données directement depuis la table enhanced
            df = self.cleaner.load_data_from_enhanced()
            if df.empty:
                self.logger.warning("Aucune donnée trouvée dans la table enhanced")
                return None

            # Exporter en CSV
            csv_path = self.cleaner.export_enhanced_to_csv(df)
            self.logger.info(f"Données enhanced exportées vers {csv_path}")
            return csv_path
        except Exception as e:
            self.logger.error(f" Erreur lors de l'export enhanced : {e}")
            return None

    def run_full_pipeline(self) -> Dict[str, bool]:
        """
        Exécute l'ensemble du pipeline de données, étape par étape.

        Returns:
            Dict[str, bool]: Dictionnaire indiquant le statut de chaque étape.

        Exemple d'utilisation :
            pipeline = DataPipelineManager()
            results = pipeline.run_full_pipeline()
        """
        results = {
            "reset_database": False,
            "spiders": False,
            "clean_and_enhance": False,
            "export_enhanced": False,
        }

        try:
            # 1. Réinitialiser la base de données
            self.logger.info("🔄 Réinitialisation de la base de données...")
            if not reset_database():
                self.logger.error(" Échec de la réinitialisation de la base de données")
                return results
            results["reset_database"] = True

            # 2. Lancer les spiders
            if not self.run_spiders():
                self.logger.error(" Échec des spiders")
                return results
            results["spiders"] = True

            # 3. Nettoyer et enrichir les données
            if not self.clean_and_enhance_data():
                self.logger.error(" Échec du nettoyage et de l'enrichissement des données")
                return results
            results["clean_and_enhance"] = True

            # 4. Exporter les données enrichies
            csv_path = self.export_enhanced_data()
            if not csv_path:
                self.logger.error(" Échec de l'export des données enrichies")
                return results
            results["export_enhanced"] = True

            self.logger.info("Pipeline terminé avec succès!")
            return results

        except Exception as e:
            self.logger.error(f" Erreur dans le pipeline : {e}")
            return results


def main():
    """
    Point d'entrée principal du script pipeline_manager.py.
    Instancie le pipeline, exécute le pipeline complet et affiche un résumé des résultats.

    Returns:
        int: 0 si tout a réussi, 1 sinon (pour usage en ligne de commande).

    Exemple d'utilisation :
        python pipeline_manager.py
    """
    try:
        pipeline = DataPipelineManager()
        results = pipeline.run_full_pipeline()

        # Afficher le résumé des résultats
        print("\nRésumé du pipeline :")
        print("=" * 50)
        for step, success in results.items():
            status = "V" if success else "X"
            print(f"{status} {step}")

        # Retourner un code d'erreur si une étape a échoué
        return 0 if all(results.values()) else 1

    except Exception as e:
        print(f"Erreur critique : {e}")
        return 1


if __name__ == "__main__":
    exit(main())
