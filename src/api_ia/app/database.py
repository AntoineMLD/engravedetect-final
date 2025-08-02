import json
import logging
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# Configuration du logging
logger = logging.getLogger(__name__)

# Liste des tags Top 20 possibles (symboles de gravures)
TOP20_TAGS = [
    '^', '1sl', 'ae', 'arc', 'balance', 'carré', 'cercle', 'cintre', 'coupe', 'coureur',
    'csl', 'doubletriangle', 'e_accentdouble', 'eas', 'e_coeur', 'e_courbe', 'e_courbebasse',
    'e_oeil', 'e_soleil', 'e)', 'e)_', 'ea', 'epsilone', 'étoile', 'figma', 'fleche',
    'hexagone', 'isi', 'losange', 'losange-triangle-carre-cercle', 'lune', 'm_symbol',
    'machine_laver', 'manette', 'n_encoche', 'neo', 'neutron', 'notemusique',
    'o_courbebasse', 'oeil_a', 'oeilprofil', 'omega', 'ordi', 'pi', 'pont', 'road',
    '(e', '(e)', '(s)', '{s}', 's1', 'sigma', 'soleil', 'tortue', 'triangle',
    'triangle-carre', 'triangle-carre-cercle', 'vcercle', 'wifi', 'wifi_rectangle',
    '_ea_', '_x_', '---e', '[sl', 's_carre', 's_cercle', 's_losange'
]

# Initialisation SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    """
    Gestionnaire de contexte pour obtenir une session SQLAlchemy.

    Yields:
        Session: Session SQLAlchemy connectée à la base.

    Exemple d'utilisation :
        with get_db_session() as db:
            result = db.execute(...)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_query(query: str, params: dict = None) -> List[Any]:
    """
    Exécute une requête SQL avec SQLAlchemy et retourne les résultats.

    Args:
        query (str): Requête SQL à exécuter.
        params (dict, optionnel): Paramètres de la requête.

    Returns:
        List[Any]: Résultats de la requête (listes de tuples).

    Raises:
        Exception: Si l'exécution échoue.

    Exemple d'utilisation :
        results = execute_query('SELECT * FROM verres')
    """
    try:
        with get_db_session() as db:
            result = db.execute(text(query), params or {})
            return result.fetchall()
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la requête: {e}")
        raise


def parse_verre_tags(tags_json: str) -> List[str]:
    """
    Parse une chaîne JSON représentant une liste de tags.

    Args:
        tags_json (str): Chaîne JSON à parser.

    Returns:
        List[str]: Liste de tags extraits.

    Exemple d'utilisation :
        tags = parse_verre_tags('["tag1", "tag2"]')
    """
    try:
        return json.loads(tags_json or "[]")
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON pour les tags: {e}")
        return []


def create_verre_dict(row: Any, columns: List[str]) -> Dict[str, Any]:
    """
    Transforme une ligne SQL (tuple) et une liste de colonnes en dictionnaire.

    Args:
        row (Any): Tuple représentant une ligne SQL.
        columns (List[str]): Liste des noms de colonnes.

    Returns:
        Dict[str, Any]: Dictionnaire clé-valeur pour chaque colonne.

    Exemple d'utilisation :
        d = create_verre_dict(row, result.keys())
    """
    verre = dict(zip(columns, row))
    if "tags" in verre:
        verre["tags"] = parse_verre_tags(verre["tags"])
    return verre


def filter_top20_tags(tags: List[str]) -> List[str]:
    """
    Filtre une liste de tags pour ne garder que ceux du Top 20.

    Args:
        tags (List[str]): Liste de tags à filtrer.

    Returns:
        List[str]: Tags appartenant au Top 20.
    """
    return [tag for tag in tags if tag in TOP20_TAGS]


def filter_manual_tags(tags: List[str]) -> List[str]:
    """
    Filtre une liste de tags pour ne garder que ceux qui ne sont PAS du Top 20.

    Args:
        tags (List[str]): Liste de tags à filtrer.

    Returns:
        List[str]: Tags n'appartenant pas au Top 20.
    """
    return [tag for tag in tags if tag not in TOP20_TAGS]


def find_matching_verres(tags: List[str]) -> List[Dict[str, Any]]:
    """
    Trouve les verres correspondant à une liste de tags selon une logique intelligente :
    - Sépare automatiquement les tags Top 20 des tags manuels
    - Si tags Top 20 présents : recherche OR parmi Top 20 + filtre par tags manuels
    - Sinon : recherche AND classique

    Args:
        tags (List[str]): Liste de tags à rechercher.

    Returns:
        List[Dict[str, Any]]: Liste de verres correspondants (dictionnaires).

    Exemple d'utilisation :
        verres = find_matching_verres(['cercle', 'marque'])
    """
    try:
        if not tags:
            return []

        # Séparation automatique des tags
        top20_tags = filter_top20_tags(tags)
        manual_tags = filter_manual_tags(tags)
        
        logger.info(f"Tags Top 20 détectés: {top20_tags}")
        logger.info(f"Tags manuels détectés: {manual_tags}")

        query = """
            SELECT v.id, v.nom, v.variante, v.hauteur_min, v.hauteur_max,
                   v.indice, v.gravure, v.url_source, v.fournisseur, v.tags
            FROM verres v
            WHERE v.tags IS NOT NULL
        """
        results = execute_query(query)

        verres = []
        for row in results:
            try:
                verre_tags = parse_verre_tags(row[9])
                verre_tags_lower = [vt.strip().lower() for vt in verre_tags]
                manual_tags_lower = [tag.strip().lower() for tag in manual_tags]
                
                # Logique avec conditions simples
                if top20_tags:
                    # Mode Top 20 : OR parmi Top 20 + AND pour tags manuels
                    top20_tags_lower = [tag.strip().lower() for tag in top20_tags]
                    
                    # Condition 1 : Le verre doit avoir au moins un tag du Top 20
                    has_top20_tag = any(tag in verre_tags_lower for tag in top20_tags_lower)
                    
                    # Condition 2 : Le verre doit avoir tous les tags manuels (si il y en a)
                    has_all_manual_tags = True
                    if manual_tags_lower:
                        has_all_manual_tags = all(tag in verre_tags_lower for tag in manual_tags_lower)
                    
                    # Les deux conditions doivent être vraies
                    if has_top20_tag and has_all_manual_tags:
                        verres.append({
                            "id": row[0],
                            "nom": row[1],
                            "indice": row[5],
                            "gravure": row[6],
                            "url_source": row[7],
                            "fournisseur": row[8],
                            "tags": verre_tags,
                            "matching_tags": [tag for tag in manual_tags_lower if tag in verre_tags_lower]
                        })
                else:
                    # Mode classique : tous les tags doivent être présents (AND)
                    if manual_tags_lower and all(tag in verre_tags_lower for tag in manual_tags_lower):
                        verres.append({
                            "id": row[0],
                            "nom": row[1],
                            "indice": row[5],
                            "gravure": row[6],
                            "url_source": row[7],
                            "fournisseur": row[8],
                            "tags": verre_tags,
                            "matching_tags": [tag for tag in manual_tags_lower if tag in verre_tags_lower]
                        })
            except Exception as e:
                logger.error(f"Erreur lors du traitement des tags pour le verre {row[0]}: {e}")
                continue

        if top20_tags:
            logger.info(f"Nombre de verres avec tags Top 20 + filtres manuels: {len(verres)}")
        else:
            logger.info(f"Nombre de verres ayant TOUS les tags correspondants: {len(verres)}")
        return verres

    except Exception as e:
        logger.error(f"Erreur lors de la recherche des verres: {e}")
        return []


def get_verre_details(verre_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère les détails d’un verre par son ID depuis la table principale.

    Args:
        verre_id (int): Identifiant du verre à rechercher.

    Returns:
        Optional[Dict[str, Any]]: Dictionnaire des détails du verre ou None si non trouvé.

    Exemple d'utilisation :
        details = get_verre_details(42)
    """
    try:
        query = "SELECT * FROM verres WHERE id = :verre_id"
        with get_db_session() as db:
            result = db.execute(text(query), {"verre_id": verre_id})
            row = result.fetchone()
            if not row:
                logger.warning(f"Verre avec ID {verre_id} non trouvé")
                return None
            return create_verre_dict(row, result.keys())
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails du verre: {e}")
        return None


def get_verre_staging_details(verre_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère les détails d’un verre par son ID depuis la table staging.

    Args:
        verre_id (int): Identifiant du verre à rechercher dans la table staging.

    Returns:
        Optional[Dict[str, Any]]: Dictionnaire des détails du verre ou None si non trouvé.

    Exemple d'utilisation :
        details = get_verre_staging_details(42)
    """
    try:
        query = "SELECT * FROM verres_staging WHERE id = :verre_id"
        with get_db_session() as db:
            result = db.execute(text(query), {"verre_id": verre_id})
            row = result.fetchone()
            if not row:
                logger.warning(f"Verre staging avec ID {verre_id} non trouvé")
                return None
            return create_verre_dict(row, result.keys())
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du verre staging: {e}")
        return None


def delete_user_by_username(username: str) -> bool:
    """
    Supprime un utilisateur de la table users par son nom d'utilisateur.

    Args:
        username (str): Nom d'utilisateur à supprimer.

    Returns:
        bool: True si l'utilisateur a été supprimé, False sinon.

    Exemple d'utilisation :
        success = delete_user_by_username('admin')
    """
    try:
        with get_db_session() as db:
            result = db.execute(text("DELETE FROM users WHERE username = :username"), {"username": username})
            db.commit()
            return result.rowcount > 0
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'utilisateur {username}: {e}")
        return False
