# src/scripts/insert_tags.py

import os
import json
import logging
from typing import List, Dict
import psycopg2
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    """Établit une connexion à PostgreSQL."""
    load_dotenv()
    try:
        return psycopg2.connect(os.getenv("DATABASE_URL"))
    except Exception as error:
        logger.error(f"❌ Erreur de connexion PostgreSQL : {error}")
        raise


def load_tags_from_json() -> List[Dict]:
    """Charge les tags depuis le fichier JSON."""
    try:
        with open("output/verres_tags.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as error:
        logger.error(f"❌ Erreur lors de la lecture du fichier JSON : {error}")
        raise


def update_tags_in_database(conn, tags_data: List[Dict]):
    """Met à jour les tags dans la table verres."""
    cursor = conn.cursor()
    updated_count = 0
    error_count = 0

    for item in tags_data:
        try:
            tags_json = json.dumps(item["tags"], ensure_ascii=False)

            # PostgreSQL utilise %s au lieu de ?
            query = """
                UPDATE verres
                SET tags = %s
                WHERE gravure ILIKE %s
            """
            cursor.execute(query, (tags_json, f"%{item['gravure']}%"))

            if cursor.rowcount > 0:
                updated_count += 1
                logger.info(f"✅ Tags mis à jour pour : {item['gravure']}")
            else:
                logger.warning(f"⚠️ Aucune correspondance trouvée pour : {item['gravure']}")

        except Exception as error:
            error_count += 1
            logger.error(f"❌ Erreur pour {item['gravure']} : {error}")

    conn.commit()
    logger.info(f"🔄 Résultat : {updated_count} mis à jour, {error_count} erreurs.")


def main():
    try:
        logger.info("📥 Chargement des tags JSON...")
        tags_data = load_tags_from_json()

        logger.info("🔌 Connexion PostgreSQL...")
        conn = get_connection()

        logger.info("📤 Insertion des tags dans la base de données...")
        update_tags_in_database(conn, tags_data)

        conn.close()
        logger.info("✅ Opération terminée avec succès !")

    except Exception as error:
        logger.error(f"❌ Une erreur est survenue : {error}")
        raise


if __name__ == "__main__":
    main()
