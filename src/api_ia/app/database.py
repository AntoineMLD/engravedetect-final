import json
import os
import logging
import pyodbc
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
from .config import AZURE_SERVER, AZURE_DATABASE, AZURE_USERNAME, AZURE_PASSWORD, AZURE_DRIVER

# Configuration du logging
logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """
    Gestionnaire de contexte pour la connexion à la base de données Azure.

    Yields:
        pyodbc.Connection: Objet de connexion à la base de données.

    Raises:
        pyodbc.Error: Si la connexion échoue.
    """
    conn = None
    try:
        conn_str = (
            f"DRIVER={AZURE_DRIVER};"
            f"SERVER={AZURE_SERVER};"
            f"DATABASE={AZURE_DATABASE};"
            f"UID={AZURE_USERNAME};"
            f"PWD={AZURE_PASSWORD};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
        )
        conn = pyodbc.connect(conn_str)
        yield conn
    except pyodbc.Error as e:
        logger.error(f"Erreur de connexion à la base de données Azure: {e}")
        raise
    finally:
        if conn:
            conn.close()


def execute_query(query: str, params: tuple = None) -> List[tuple]:
    """
    Exécute une requête SQL avec des paramètres.

    Args:
        query (str): Requête SQL à exécuter.
        params (tuple, optional): Paramètres de la requête.

    Returns:
        List[tuple]: Résultats de la requête.

    Raises:
        pyodbc.Error: Si l'exécution de la requête échoue.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    except pyodbc.Error as e:
        logger.error(f"Erreur lors de l'exécution de la requête: {e}")
        raise


def parse_verre_tags(tags_json: str) -> List[str]:
    """
    Parse les tags JSON d'un verre.

    Args:
        tags_json (str): Tags au format JSON.

    Returns:
        List[str]: Liste des tags.
    """
    try:
        return json.loads(tags_json or "[]")
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON pour les tags: {e}")
        return []


def create_verre_dict(row: tuple, columns: List[str]) -> Dict[str, Any]:
    """
    Crée un dictionnaire pour un verre à partir d'une ligne de la base de données.

    Args:
        row (tuple): Ligne de la base de données.
        columns (List[str]): Noms des colonnes.

    Returns:
        Dict[str, Any]: Dictionnaire représentant le verre.
    """
    verre = dict(zip(columns, row))
    if "tags" in verre:
        verre["tags"] = parse_verre_tags(verre["tags"])
    return verre


def find_matching_verres(tags: List[str]) -> List[Dict[str, Any]]:
    """
    Trouve les verres correspondant aux tags donnés.

    Args:
        tags (list): Liste de tags à rechercher.

    Returns:
        list: Liste des verres correspondant aux tags.
    """
    try:
        if not tags:
            return []

        # Récupérer tous les verres avec leurs tags
        query = """
            SELECT v.id, v.nom, v.variante, v.hauteur_min, v.hauteur_max,
                   v.indice, v.gravure, v.url_source, v.fournisseur, v.tags
            FROM verres v
            WHERE v.tags IS NOT NULL
        """

        results = execute_query(query)
        logger.info(f"Nombre total de verres trouvés: {len(results)}")

        # Filtrer les verres qui ont exactement les tags recherchés
        verres = []
        for row in results:
            verre_id, nom, variante, hauteur_min, hauteur_max, indice, gravure, url_source, fournisseur, tags_json = row
            try:
                # Parser les tags du verre
                verre_tags = parse_verre_tags(tags_json)

                # Convertir tous les tags en minuscules pour la comparaison
                verre_tags_lower = [vt.strip().lower() for vt in verre_tags]
                search_tags_lower = [tag.strip().lower() for tag in tags]

                # Vérifier que TOUS les tags recherchés sont présents
                if all(tag in verre_tags_lower for tag in search_tags_lower):
                    verres.append(
                        {
                            "id": verre_id,
                            "nom": nom,
                            "indice": indice,
                            "gravure": gravure,
                            "url_source": url_source,
                            "fournisseur": fournisseur,
                            "tags": verre_tags,  # Garder les tags originaux dans la réponse
                        }
                    )
            except Exception as e:
                logger.error(f"Erreur lors du traitement des tags pour le verre {verre_id}: {e}")
                continue

        logger.info(f"Nombre de verres correspondant aux tags: {len(verres)}")
        return verres

    except Exception as e:
        logger.error(f"Erreur lors de la recherche des verres: {e}")
        return []


def get_verre_details(verre_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère les détails complets d'un verre.

    Args:
        verre_id (int): Identifiant du verre.

    Returns:
        Optional[Dict[str, Any]]: Détails du verre ou None si non trouvé.
    """
    try:
        # Requête SQL optimisée pour Azure
        query = """
            SELECT *
            FROM verres
            WHERE id = @verre_id
        """

        results = execute_query(query, (verre_id,))
        if not results:
            logger.warning(f"Verre avec ID {verre_id} non trouvé")
            return None

        with get_db_connection() as conn:
            cursor = conn.cursor()
            columns = [column[0] for column in cursor.description]
            return create_verre_dict(results[0], columns)

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails du verre: {e}")
        return None


def get_verre_staging_details(verre_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère les détails d'un verre depuis la table staging.

    Args:
        verre_id (int): Identifiant du verre.

    Returns:
        Optional[Dict[str, Any]]: Détails du verre ou None si non trouvé.
    """
    try:
        # Requête SQL optimisée pour Azure
        query = """
            SELECT *
            FROM verres_staging
            WHERE id = @verre_id
        """

        results = execute_query(query, (verre_id,))
        if not results:
            logger.warning(f"Verre staging avec ID {verre_id} non trouvé")
            return None

        with get_db_connection() as conn:
            cursor = conn.cursor()
            columns = [column[0] for column in cursor.description]
            return create_verre_dict(results[0], columns)

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails du verre staging: {e}")
        return None
