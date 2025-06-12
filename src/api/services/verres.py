from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, distinct
from typing import Optional, List
from ..schemas.verres import VerreFilters, VerreResponse, VerreList
from ..models.references import Fournisseur, Materiau, Gamme, Serie
from ..models.verres import Verre

def get_verres(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[VerreFilters] = None
) -> VerreList:
    """Récupère la liste des verres avec filtres optionnels."""
    # Utilisation de joinedload pour charger les relations
    query = db.query(Verre).options(
        joinedload(Verre.fournisseur),
        joinedload(Verre.materiau)
    )

    if filters:
        # Application des filtres
        if filters.fournisseur:
            query = query.filter(Verre.fournisseur.has(nom=filters.fournisseur))
        if filters.materiau:
            query = query.filter(Verre.materiau.has(nom=filters.materiau))
        if filters.gamme:
            query = query.filter(Verre.gamme == filters.gamme)
        if filters.serie:
            query = query.filter(Verre.serie == filters.serie)
        if filters.indice_min is not None:
            query = query.filter(Verre.indice >= filters.indice_min)
        if filters.indice_max is not None:
            query = query.filter(Verre.indice <= filters.indice_max)
        if filters.protection is not None:
            query = query.filter(Verre.protection == filters.protection)
        if filters.photochromic is not None:
            query = query.filter(Verre.photochromic == filters.photochromic)

    total = query.count()
    items = query.order_by(Verre.id).offset(skip).limit(limit).all()
    
    # Conversion des objets SQLAlchemy en schémas Pydantic
    verre_responses = [VerreResponse.model_validate(verre) for verre in items]
    
    return VerreList(total=total, items=verre_responses)

def get_verre(db: Session, verre_id: int):
    """Récupère un verre par son ID."""
    return db.query(Verre).options(
        joinedload(Verre.fournisseur),
        joinedload(Verre.materiau)
    ).filter(Verre.id == verre_id).first()

def get_fournisseurs(db: Session) -> List[str]:
    """Récupère la liste des noms de fournisseurs."""
    return [f[0] for f in db.query(Fournisseur.nom).distinct().all()]

def get_materiaux(db: Session) -> List[str]:
    """Récupère la liste des noms de matériaux."""
    return [m[0] for m in db.query(Materiau.nom).distinct().all()]

def get_gammes(db: Session) -> List[str]:
    """Récupère la liste des noms de gammes."""
    return [g[0] for g in db.query(Gamme.nom).distinct().all()]

def get_series(db: Session) -> List[str]:
    """Récupère la liste des noms de séries."""
    return [s[0] for s in db.query(Serie.nom).distinct().all()]

def get_stats(db: Session) -> dict:
    """Récupère les statistiques générales."""
    return {
        "total_verres": db.query(Verre).count(),
        "total_fournisseurs": db.query(Fournisseur).distinct().count(),
        "total_materiaux": db.query(Materiau).distinct().count(),
        "total_gammes": db.query(Gamme).distinct().count(),
        "total_series": db.query(Serie).distinct().count(),
    } 