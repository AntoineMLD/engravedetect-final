from pydantic import BaseModel, Field
from typing import Optional, List

class FournisseurResponse(BaseModel):
    nom: str = Field(..., description="Nom du fournisseur")
    
    class Config:
        from_attributes = True

class MateriauResponse(BaseModel):
    nom: str = Field(..., description="Type de matériau")
    
    class Config:
        from_attributes = True

class VerreBase(BaseModel):
    nom: str = Field(..., description="Nom du verre")
    variante: Optional[str] = Field(None, description="Type de variante (STANDARD, COURT)")
    hauteur_min: Optional[int] = Field(None, description="Hauteur minimale en mm")
    hauteur_max: Optional[int] = Field(None, description="Hauteur maximale en mm")
    indice: Optional[float] = Field(None, description="Indice de réfraction")
    gravure: Optional[str] = Field(None, description="Code de gravure nasale")
    protection: Optional[bool] = Field(None, description="Présence de protection (UV, Blue)")
    photochromic: Optional[bool] = Field(None, description="Verre photochromique")

    class Config:
        from_attributes = True

class VerreResponse(VerreBase):
    id: int
    fournisseur: Optional[FournisseurResponse] = Field(None, description="Informations du fournisseur")
    materiau: Optional[MateriauResponse] = Field(None, description="Informations du matériau")
    gamme: Optional[str] = Field(None, description="Gamme du produit")
    serie: Optional[str] = Field(None, description="Série du produit")

class VerreList(BaseModel):
    total: int = Field(..., description="Nombre total de verres")
    items: List[VerreResponse]

class VerreFilters(BaseModel):
    fournisseur: Optional[str] = None
    materiau: Optional[str] = None
    gamme: Optional[str] = None
    serie: Optional[str] = None
    indice_min: Optional[float] = None
    indice_max: Optional[float] = None
    protection: Optional[bool] = None
    photochromic: Optional[bool] = None 