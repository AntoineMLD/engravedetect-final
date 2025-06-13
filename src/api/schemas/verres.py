from pydantic import BaseModel, Field
from typing import Optional, List


class VerreBase(BaseModel):
    nom: str = Field(..., description="Nom du verre")
    materiaux: Optional[str] = Field(None, description="Type de matériau")
    indice: Optional[float] = Field(None, description="Indice de réfraction")
    fournisseur: Optional[str] = Field(None, description="Nom du fournisseur")
    gravure: Optional[str] = Field(None, description="Code de gravure nasale")
    url_source: Optional[str] = Field(None, description="URL source")
    variante: Optional[str] = Field(None, description="Type de variante (STANDARD, COURT)")
    hauteur_min: Optional[int] = Field(None, description="Hauteur minimale en mm")
    hauteur_max: Optional[int] = Field(None, description="Hauteur maximale en mm")
    protection: Optional[bool] = Field(None, description="Présence de protection (UV, Blue)")
    photochromic: Optional[bool] = Field(None, description="Verre photochromique")
    tags: Optional[str] = Field(None, description="Tags extraits du nom")
    image_gravure: Optional[str] = Field(None, description="Chemin vers l'image de la gravure")

    class Config:
        from_attributes = True


class VerreResponse(VerreBase):
    id: int


class VerreList(BaseModel):
    total: int = Field(..., description="Nombre total de verres")
    items: List[VerreResponse]


class VerreFilters(BaseModel):
    fournisseur: Optional[str] = None
    materiaux: Optional[str] = None
    indice_min: Optional[float] = None
    indice_max: Optional[float] = None
    protection: Optional[bool] = None
    photochromic: Optional[bool] = None
