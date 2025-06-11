import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import scrapy

class DataPipelineManager:
    """
    Orchestrateur principal du pipeline de données optiques.
    Gère l'ensemble du flux de données : du scraping à la création des tables finales.
    """
    
    def __init__(self):
        self._setup_logging()
        self._load_dependencies()
        
    def _setup_logging(self) -> None:
        """Configure le système de logging."""
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
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def _load_dependencies(self) -> None:
        """Charge les dépendances nécessaires."""
        try:
            from src.data.scraping.france_optique.spiders import (
                glass_spider_hoya,
                glass_spider_full_xpath,
                glass_spider_particular,
                glass_spider_optovision,
                glass_spider_indo_optical
            )
            from src.data.processing.cleaner import OpticalDataCleaner
            from src.database.models.tables import DatabaseManager
            
            self.spiders = {
                'hoya': glass_spider_hoya,
                'full_xpath': glass_spider_full_xpath,
                'particular': glass_spider_particular,
                'optovision': glass_spider_optovision,
                'indo_optical': glass_spider_indo_optical
            }
            
            self.cleaner = OpticalDataCleaner()
            self.db_manager = DatabaseManager()
            
            self.logger.info("✅ Dépendances chargées avec succès")
            
        except ImportError as e:
            self.logger.error(f"❌ Erreur lors du chargement des dépendances : {e}")
            raise
            
    def run_spiders(self) -> bool:
        """
        Lance tous les spiders pour collecter les données.
        
        Returns:
            bool: True si tous les spiders ont réussi, False sinon
        """
        self.logger.info("🕷️ Démarrage des spiders...")
        
        try:
            from scrapy.crawler import CrawlerProcess
            from scrapy.utils.project import get_project_settings
            
            process = CrawlerProcess(get_project_settings())
            
            # Ajouter chaque spider au processus
            for spider_name, spider_module in self.spiders.items():
                self.logger.info(f"➕ Ajout du spider {spider_name}")
                # Obtenir la classe Spider directement du module
                spider_class = next(obj for name, obj in spider_module.__dict__.items() 
                                  if isinstance(obj, type) and issubclass(obj, scrapy.Spider))
                process.crawl(spider_class)
            
            # Lancer tous les spiders
            process.start()
            
            self.logger.info("✅ Tous les spiders ont terminé avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'exécution des spiders : {e}")
            return False
            
    def export_staging_data(self) -> Optional[str]:
        """
        Exporte les données de la table staging en CSV.
        
        Returns:
            Optional[str]: Chemin du fichier CSV généré ou None en cas d'erreur
        """
        self.logger.info("📤 Export des données staging en CSV...")
        try:
            # Charger les données de staging
            df = self.cleaner.load_data_from_staging()
            # Exporter en CSV
            csv_path = self.cleaner.export_to_csv(df)
            self.logger.info(f"✅ Données staging exportées vers {csv_path}")
            return csv_path
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'export staging : {e}")
            return None
            
    def clean_and_enhance_data(self) -> bool:
        """
        Nettoie les données et les insère dans la table enhanced.
        
        Returns:
            bool: True si le processus a réussi, False sinon
        """
        self.logger.info("🧹 Nettoyage et amélioration des données...")
        try:
            # Charger et nettoyer les données
            df_raw = self.cleaner.load_data_from_staging()
            df_clean = self.cleaner.clean_dataframe(df_raw)
            
            # Créer la table enhanced et insérer les données
            self.cleaner.create_enhanced_table()
            self.cleaner.insert_to_enhanced(df_clean)
            
            # Afficher les statistiques
            self.cleaner.get_data_statistics(df_clean)
            
            self.logger.info("✅ Données nettoyées et améliorées avec succès")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du nettoyage des données : {e}")
            return False
            
    def export_enhanced_data(self) -> Optional[str]:
        """
        Exporte les données de la table enhanced en CSV.
        
        Returns:
            Optional[str]: Chemin du fichier CSV généré ou None en cas d'erreur
        """
        self.logger.info("📤 Export des données enhanced en CSV...")
        try:
            # Charger les données de la table enhanced
            df = self.cleaner.load_data_from_staging()  # On charge d'abord les données brutes
            df_clean = self.cleaner.clean_dataframe(df)  # On les nettoie
            # Exporter en CSV
            csv_path = self.cleaner.export_enhanced_to_csv(df_clean)
            self.logger.info(f"✅ Données enhanced exportées vers {csv_path}")
            return csv_path
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'export enhanced : {e}")
            return None
            
    def create_main_tables(self) -> bool:
        """
        Crée les tables principales et y insère les données.
        
        Returns:
            bool: True si le processus a réussi, False sinon
        """
        self.logger.info("🏗️ Création des tables principales...")
        try:
            self.db_manager.process()
            self.logger.info("✅ Tables principales créées avec succès")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la création des tables principales : {e}")
            return False
            
    def run_full_pipeline(self) -> Dict[str, bool]:
        """
        Exécute l'ensemble du pipeline de données.
        
        Returns:
            Dict[str, bool]: Statut de chaque étape du pipeline
        """
        self.logger.info("🚀 Démarrage du pipeline complet...")
        self.logger.info("=" * 80)
        
        results = {
            "spiders": False,
            "staging_export": False,
            "data_cleaning": False,
            "enhanced_export": False,
            "main_tables": False
        }
        
        # 1. Lancer les spiders
        results["spiders"] = self.run_spiders()
        if not results["spiders"]:
            self.logger.error("⛔ Arrêt du pipeline : échec des spiders")
            return results
            
        # 2. Exporter les données staging
        staging_csv = self.export_staging_data()
        results["staging_export"] = staging_csv is not None
        
        # 3. Nettoyer et améliorer les données
        results["data_cleaning"] = self.clean_and_enhance_data()
        if not results["data_cleaning"]:
            self.logger.error("⛔ Arrêt du pipeline : échec du nettoyage des données")
            return results
            
        # 4. Exporter les données enhanced
        enhanced_csv = self.export_enhanced_data()
        results["enhanced_export"] = enhanced_csv is not None
        
        # 5. Créer les tables principales
        results["main_tables"] = self.create_main_tables()
        
        # Résumé final
        self.logger.info("=" * 80)
        self.logger.info("📊 Résumé du pipeline :")
        for step, success in results.items():
            status = "✅" if success else "❌"
            self.logger.info(f"{status} {step}")
        
        return results

def main():
    """Point d'entrée principal du script."""
    try:
        pipeline = DataPipelineManager()
        results = pipeline.run_full_pipeline()
        
        # Vérifier si toutes les étapes ont réussi
        if all(results.values()):
            logging.info("✨ Pipeline terminé avec succès !")
            return 0
        else:
            logging.error("⚠️ Pipeline terminé avec des erreurs.")
            return 1
            
    except Exception as e:
        logging.error(f"❌ Erreur fatale dans le pipeline : {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 