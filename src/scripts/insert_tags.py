"""
Script d'insertion des tags extraits dans la base de données PostgreSQL.

Ce module charge les tags extraits depuis un fichier JSON et les insère
dans la table verres de la base de données PostgreSQL.

Fonctionnalités :
- Chargement des tags depuis le fichier JSON
- Connexion sécurisée à PostgreSQL
- Mise à jour en lot des enregistrements
- Gestion des erreurs et logging détaillé
- Validation des correspondances de gravures

Processus :
1. Lecture du fichier output/verres_tags.json
2. Connexion à la base PostgreSQL
3. Mise à jour des tags pour chaque gravure
4. Validation et reporting des résultats

Format des données :
- Tags stockés en JSON dans la colonne tags
- Correspondance par gravure (recherche ILIKE)
- Gestion des caractères spéciaux (UTF-8)

Auteur : Équipe de développement
Version : 1.0.0
"""

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
    """
    Établit une connexion à la base de données PostgreSQL à partir de la variable d'environnement DATABASE_URL.

    Returns:
        connection (psycopg2.extensions.connection): Objet de connexion PostgreSQL.

    Raises:
        Exception: Si la connexion échoue.

    Exemple d'utilisation :
        conn = get_connection()
    """
    load_dotenv()
    try:
        return psycopg2.connect(os.getenv("DATABASE_URL"))
    except Exception as error:
        logger.error(f"❌ Erreur de connexion PostgreSQL : {error}")
        raise


def load_tags_from_json() -> List[Dict]:
    """
    Charge les tags extraits depuis le fichier JSON généré par extract_tags.py.

    Returns:
        List[Dict]: Liste de dictionnaires contenant les gravures et leurs tags associés.

    Raises:
        Exception: Si la lecture du fichier JSON échoue.

    Exemple d'utilisation :
        tags_data = load_tags_from_json()
    """
    try:
        with open("output/verres_tags.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as error:
        logger.error(f"❌ Erreur lors de la lecture du fichier JSON : {error}")
        raise


def update_tags_in_database(conn, tags_data: List[Dict]):
    """
    Met à jour la colonne 'tags' de la table 'verres' pour chaque gravure présente dans tags_data.

    Args:
        conn: Objet de connexion PostgreSQL.
        tags_data (List[Dict]): Liste de dictionnaires avec les champs 'gravure' et 'tags'.

    Cette fonction parcourt chaque entrée, convertit les tags en JSON, et met à jour la base.
    Elle logue le nombre de mises à jour et d'erreurs.

    Exemple d'utilisation :
        conn = get_connection()
        tags_data = load_tags_from_json()
        update_tags_in_database(conn, tags_data)
    """
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
    """
    Point d'entrée du script. Charge les tags, se connecte à la base et met à jour les enregistrements.

    Étapes :
    1. Chargement des tags depuis le JSON
    2. Connexion à PostgreSQL
    3. Mise à jour des tags dans la base
    4. Fermeture de la connexion

    Exemple d'utilisation :
        python insert_tags.py
    """
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
