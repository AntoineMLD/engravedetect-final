from pydantic import BaseModel, Field
from typing import Optional, List


class VerreBase(BaseModel):
    """Schéma de base pour les verres."""
    nom: str = Field(..., description="Nom du verre")
    fournisseur: str = Field(..., description="Fournisseur du verre")
    materiaux: str = Field(..., description="Matériau du verre")
    indice: float = Field(..., description="Indice de réfraction")
    protection: bool = Field(False, description="Présence de protection")
    photochromic: bool = Field(False, description="Verre photochromique")
    hauteur_min: Optional[float] = Field(None, description="Hauteur minimale en mm")
    hauteur_max: Optional[float] = Field(None, description="Hauteur maximale en mm")
    gravure: Optional[str] = Field(None, description="Code de gravure nasale")


class VerreCreate(VerreBase):
    """Schéma pour la création d'un verre."""
    pass


class VerreUpdate(BaseModel):
    """Schéma pour la mise à jour d'un verre."""
    nom: Optional[str] = Field(None, description="Nom du verre")
    fournisseur: Optional[str] = Field(None, description="Fournisseur du verre")
    materiaux: Optional[str] = Field(None, description="Matériau du verre")
    indice: Optional[float] = Field(None, description="Indice de réfraction")
    protection: Optional[bool] = Field(None, description="Présence de protection")
    photochromic: Optional[bool] = Field(None, description="Verre photochromique")
    hauteur_min: Optional[float] = Field(None, description="Hauteur minimale en mm")
    hauteur_max: Optional[float] = Field(None, description="Hauteur maximale en mm")
    gravure: Optional[str] = Field(None, description="Code de gravure nasale")


class VerreResponse(VerreBase):
    """Schéma de réponse pour un verre."""
    id: int = Field(..., description="Identifiant unique du verre")

    model_config = {"from_attributes": True}


class VerreList(BaseModel):
    """Schéma de réponse pour la liste des verres."""
    total: int = Field(..., description="Nombre total de verres")
    items: List[VerreResponse] = Field(..., description="Liste des verres")


class VerreFilters(BaseModel):
    """Schéma pour les filtres de recherche."""
    fournisseur: Optional[str] = None
    materiaux: Optional[str] = None
    indice_min: Optional[float] = None
    indice_max: Optional[float] = None
    protection: Optional[bool] = None
    photochromic: Optional[bool] = None
