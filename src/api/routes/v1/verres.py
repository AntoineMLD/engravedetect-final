from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database.database import get_db
from ...core.auth.jwt import get_current_user
from ...services import verres as verres_service
from ...schemas.verres import VerreResponse, VerreList, VerreFilters, VerreCreate, VerreUpdate

router = APIRouter()


@router.get("/", response_model=VerreList)
async def read_verres(
    skip: int = 0,
    limit: int = 100,
    fournisseur: Optional[str] = None,
    materiaux: Optional[str] = None,
    indice_min: Optional[float] = None,
    indice_max: Optional[float] = None,
    protection: Optional[bool] = None,
    photochromic: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Liste des verres avec filtres optionnels."""
    filters = VerreFilters(
        fournisseur=fournisseur,
        materiaux=materiaux,
        indice_min=indice_min,
        indice_max=indice_max,
        protection=protection,
        photochromic=photochromic,
    )
    return verres_service.get_verres(db, skip=skip, limit=limit, filters=filters)


@router.get("/{verre_id}", response_model=VerreResponse)
async def read_verre(verre_id: int, db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    """Détails d'un verre par son ID."""
    verre = verres_service.get_verre(db, verre_id)
    if not verre:
        raise HTTPException(status_code=404, detail="Verre non trouvé")
    return verre


@router.get("/fournisseurs/list", response_model=List[str])
async def read_fournisseurs(db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    """Liste des fournisseurs."""
    return verres_service.get_fournisseurs(db)


@router.get("/materiaux/list", response_model=List[str])
async def read_materiaux(db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    """Liste des matériaux."""
    return verres_service.get_materiaux(db)


@router.get("/stats/general", response_model=dict)
async def read_stats(db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    """Statistiques générales."""
    return verres_service.get_stats(db)


@router.post("/", response_model=VerreResponse, status_code=201)
async def create_verre(verre: VerreCreate, db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    """Crée un nouveau verre."""
    return verres_service.create_verre(db, verre)


@router.put("/{verre_id}", response_model=VerreResponse)
async def update_verre(verre_id: int, verre: VerreUpdate, db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    """Met à jour un verre existant."""
    updated_verre = verres_service.update_verre(db, verre_id, verre)
    if not updated_verre:
        raise HTTPException(status_code=404, detail="Verre non trouvé")
    return updated_verre


@router.delete("/{verre_id}", status_code=204)
async def delete_verre(verre_id: int, db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    """Supprime un verre."""
    if not verres_service.delete_verre(db, verre_id):
        raise HTTPException(status_code=404, detail="Verre non trouvé")
