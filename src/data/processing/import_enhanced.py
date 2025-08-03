import logging
import os
from pathlib import Path
from src.data.processing.cleaner import OpticalDataCleaner


def main():
    """Point d'entrée pour l'import des données enhanced."""
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    try:
        # Trouver le dernier fichier CSV enhanced
        data_dir = Path("data")
        if not data_dir.exists():
            raise FileNotFoundError("Le dossier data n'existe pas")

        enhanced_files = list(data_dir.glob("enhanced_export_*.csv"))
        if not enhanced_files:
            raise FileNotFoundError("Aucun fichier enhanced_export trouvé")

        # Prendre le plus récent
        latest_file = max(enhanced_files, key=os.path.getctime)
        logger.info(f"Fichier trouvé : {latest_file}")

        # Importer les données
        cleaner = OpticalDataCleaner()
        success = cleaner.insert_from_enhanced_csv(str(latest_file))

        if success:
            logger.info("Import terminé avec succès")
            return 0
        else:
            logger.error("Import échoué")
            return 1

    except Exception as e:
        logger.error(f"Erreur : {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
