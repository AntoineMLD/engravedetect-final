from sqlalchemy import Column, Integer, String, Float, Boolean
from ..core.database.database import Base


class Verre(Base):
    """Modèle SQLAlchemy pour la table verres.
    Cette table contient les données enrichies basées sur la table enhanced.
    """

    __tablename__ = "verres"

    id = Column(Integer, primary_key=True, index=True)

    # Données de base (reprises de enhanced)
    nom = Column(String(500), nullable=False)  # Nom principal du verre
    materiaux = Column(String(100))  # Matériau brut
    indice = Column(Float)  # Indice de réfraction
    fournisseur = Column(String(200))  # Nom du fournisseur
    gravure = Column(String(1000), nullable=True)  # Gravure nasale
    url_source = Column(String(500))  # URL source

    # Données enrichies
    variante = Column(String(200))  # Variante extraite du nom
    hauteur_min = Column(Integer)  # Hauteur minimale si spécifiée
    hauteur_max = Column(Integer)  # Hauteur maximale si spécifiée
    protection = Column(Boolean, default=False)  # Si le verre a une protection (UV, Blue Light, etc)
    photochromic = Column(Boolean, default=False)  # Si le verre est photochromique
    tags = Column(String(500))  # Tags extraits du nom (JSON array as string)
    image_gravure = Column(String(500))  # Chemin vers l'image de la gravure

    class Config:
        from_attributes = True
