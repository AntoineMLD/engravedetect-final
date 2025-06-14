from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.verres import Verre
from ..schemas.verres import VerreFilters, VerreResponse, VerreList, VerreCreate, VerreUpdate


def get_verres(db: Session, filters: Optional[VerreFilters] = None, skip: int = 0, limit: int = 100) -> VerreList:
    """Récupère la liste des verres avec filtres optionnels."""
    query = db.query(Verre)

    if filters:
        # Application des filtres
        if filters.fournisseur:
            query = query.filter(Verre.fournisseur == filters.fournisseur)
        if filters.materiaux:
            query = query.filter(Verre.materiaux == filters.materiaux)
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


def get_verre(db: Session, verre_id: int) -> Optional[VerreResponse]:
    """Récupère un verre par son ID."""
    verre = db.query(Verre).filter(Verre.id == verre_id).first()
    if verre:
        return VerreResponse.model_validate(verre)
    return None


def get_fournisseurs(db: Session) -> List[str]:
    """Récupère la liste des fournisseurs distincts."""
    return [f[0] for f in db.query(Verre.fournisseur).distinct().all()]


def get_materiaux(db: Session) -> List[str]:
    """Récupère la liste des matériaux distincts."""
    return [m[0] for m in db.query(Verre.materiaux).distinct().all()]


def get_stats(db: Session) -> dict:
    """Récupère les statistiques générales."""
    return {
        "total_verres": db.query(Verre).count(),
        "total_fournisseurs": db.query(Verre.fournisseur).distinct().count(),
        "total_materiaux": db.query(Verre.materiaux).distinct().count(),
    }


def create_verre(db: Session, verre: VerreCreate) -> VerreResponse:
    """Crée un nouveau verre."""

    # Vérifications métiers simples
    if not verre.nom:
        raise ValueError("Le nom du verre est requis")
    if verre.indice <= 0:
        raise ValueError("L'indice de réfraction doit être positif")
    if verre.hauteur_min is not None and verre.hauteur_max is not None:
        if verre.hauteur_min > verre.hauteur_max:
            raise ValueError("La hauteur minimale ne peut pas être supérieure à la hauteur maximale")

    # Création et insertion en base
    db_verre = Verre(**verre.model_dump())
    db.add(db_verre)
    db.commit()
    db.refresh(db_verre)
    # Conversion en réponse Pydantic
    return VerreResponse.model_validate(db_verre)


def update_verre(db: Session, verre_id: int, verre: VerreUpdate) -> Optional[VerreResponse]:
    """Met à jour un verre existant."""
    db_verre = db.query(Verre).filter(Verre.id == verre_id).first()
    if not db_verre:
        return None

    # Mise à jour des champs non-nuls
    update_data = verre.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_verre, field, value)

    db.commit()
    db.refresh(db_verre)
    return VerreResponse.model_validate(db_verre)


def delete_verre(db: Session, verre_id: int) -> bool:
    """Supprime un verre."""
    db_verre = db.query(Verre).filter(Verre.id == verre_id).first()
    if not db_verre:
        return False

    db.delete(db_verre)
    db.commit()
    return True
