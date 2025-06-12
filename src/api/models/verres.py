from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database.database import Base


class Verre(Base):
    """Modèle SQLAlchemy pour la table verres."""
    __tablename__ = "verres"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    variante = Column(String)
    hauteur_min = Column(Integer)
    hauteur_max = Column(Integer)
    indice = Column(Float)
    gravure = Column(String)
    url_source = Column(String)
    protection = Column(Boolean, default=False)
    photochromic = Column(Boolean, default=False)
    tags = Column(String)

    # Clés étrangères
    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"))
    materiau_id = Column(Integer, ForeignKey("materiaux.id"))
    gamme_id = Column(Integer, ForeignKey("gammes.id"))
    serie_id = Column(Integer, ForeignKey("series.id"))

    # Relations
    fournisseur = relationship("Fournisseur", back_populates="verres")
    materiau = relationship("Materiau", back_populates="verres")
    gamme = relationship("Gamme", back_populates="verres")
    serie = relationship("Serie", back_populates="verres")

    class Config:
        from_attributes = True
