import json
import logging
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# Configuration du logging
logger = logging.getLogger(__name__)

# Initialisation SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    """Gestionnaire de session SQLAlchemy."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_query(query: str, params: dict = None) -> List[Any]:
    """
    Exécute une requête SQL avec SQLAlchemy.

    Args:
        query (str): Requête SQL.
        params (dict, optional): Paramètres de la requête.

    Returns:
        List[Any]: Résultats de la requête.
    """
    try:
        with get_db_session() as db:
            result = db.execute(text(query), params or {})
            return result.fetchall()
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la requête: {e}")
        raise

def parse_verre_tags(tags_json: str) -> List[str]:
    """Parse les tags JSON d'un verre."""
    try:
        return json.loads(tags_json or "[]")
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON pour les tags: {e}")
        return []

def create_verre_dict(row: Any, columns: List[str]) -> Dict[str, Any]:
    """Transforme une ligne SQL en dictionnaire."""
    verre = dict(zip(columns, row))
    if "tags" in verre:
        verre["tags"] = parse_verre_tags(verre["tags"])
    return verre

def find_matching_verres(tags: List[str], top20_tags: List[str] = None) -> List[Dict[str, Any]]:
    """
    Trouve les verres selon la logique :
    - Si top20_tags fourni : recherche OR parmi Top 20 + filtre par tags manuels
    - Sinon : recherche AND classique
    """
    try:
        if not tags and not top20_tags:
            return []

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
                search_tags_lower = [tag.strip().lower() for tag in tags]
                
                # Logique avec conditions simples
                if top20_tags:
                    # Mode Top 20 : OR parmi Top 20 + AND pour tags manuels
                    top20_tags_lower = [tag.strip().lower() for tag in top20_tags]
                    
                    # Condition 1 : Le verre doit avoir au moins un tag du Top 20
                    has_top20_tag = any(tag in verre_tags_lower for tag in top20_tags_lower)
                    
                    # Condition 2 : Le verre doit avoir tous les tags manuels (si il y en a)
                    has_all_manual_tags = True
                    if search_tags_lower:
                        has_all_manual_tags = all(tag in verre_tags_lower for tag in search_tags_lower)
                    
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
                            "matching_tags": [tag for tag in search_tags_lower if tag in verre_tags_lower]
                        })
                else:
                    # Mode classique : tous les tags doivent être présents (AND)
                    if search_tags_lower and all(tag in verre_tags_lower for tag in search_tags_lower):
                        verres.append({
                            "id": row[0],
                            "nom": row[1],
                            "indice": row[5],
                            "gravure": row[6],
                            "url_source": row[7],
                            "fournisseur": row[8],
                            "tags": verre_tags,
                            "matching_tags": [tag for tag in search_tags_lower if tag in verre_tags_lower]
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
    """Récupère les détails d’un verre par son ID."""
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
    """Récupère les détails d’un verre depuis la table staging."""
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
    """Supprime un utilisateur par son nom d'utilisateur."""
    try:
        with get_db_session() as db:
            result = db.execute(text("DELETE FROM users WHERE username = :username"), {"username": username})
            db.commit()
            return result.rowcount > 0
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'utilisateur {username}: {e}")
        return False
