import os
import json
import pyodbc
from dotenv import load_dotenv
from typing import List, Dict
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    """Établit une connexion à Azure SQL."""
    load_dotenv()
    try:
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f'SERVER={os.getenv("AZURE_SERVER")};'
            f'DATABASE={os.getenv("AZURE_DATABASE")};'
            f'UID={os.getenv("AZURE_USERNAME")};'
            f'PWD={os.getenv("AZURE_PASSWORD")};'
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        return pyodbc.connect(conn_str)
    except Exception as error:
        logger.error(f"❌ Erreur de connexion Azure SQL: {error}")
        raise


def load_tags_from_json():
    """Charge les tags depuis le fichier JSON."""
    try:
        with open("output/verres_tags.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as error:
        logger.error(f"❌ Erreur lors de la lecture du fichier JSON: {error}")
        raise


def update_tags_in_database(conn, tags_data: List[Dict]):
    """Met à jour les tags dans la base de données."""
    cursor = conn.cursor()
    updated_count = 0
    error_count = 0

    for item in tags_data:
        try:
            # Convertir la liste de tags en chaîne JSON
            tags_json = json.dumps(item["tags"], ensure_ascii=False)

            # Mettre à jour la base de données
            query = """
            UPDATE verres
            SET tags = ?
            WHERE gravure LIKE ?
            """
            # Utiliser LIKE pour faire correspondre l'URL
            cursor.execute(query, (tags_json, f"%{item['gravure']}%"))

            if cursor.rowcount > 0:
                updated_count += 1
                logger.info(f"✅ Tags mis à jour pour: {item['gravure']}")
            else:
                logger.warning(f"⚠️ Aucune correspondance trouvée pour: {item['gravure']}")

        except Exception as error:
            error_count += 1
            logger.error(f"❌ Erreur lors de la mise à jour des tags pour {item['gravure']}: {error}")

    conn.commit()
    logger.info(f"✅ Mise à jour terminée. {updated_count} enregistrements mis à jour, {error_count} erreurs.")


def main():
    try:
        # Charger les tags depuis le JSON
        logger.info("📥 Chargement des tags depuis le fichier JSON...")
        tags_data = load_tags_from_json()

        # Établir la connexion à la base de données
        logger.info("🔌 Connexion à la base de données Azure...")
        conn = get_connection()

        # Mettre à jour les tags dans la base de données
        logger.info("🔄 Mise à jour des tags dans la base de données...")
        update_tags_in_database(conn, tags_data)

        # Fermer la connexion
        conn.close()
        logger.info("✅ Opération terminée avec succès!")

    except Exception as error:
        logger.error(f"❌ Une erreur est survenue: {error}")
        raise


if __name__ == "__main__":
    main()
