from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..core.database.database import Base

class Fournisseur(Base):
    """Modèle SQLAlchemy pour la table fournisseurs."""
    __tablename__ = "fournisseurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    
    # Relations
    verres = relationship("Verre", back_populates="fournisseur")

class Materiau(Base):
    """Modèle SQLAlchemy pour la table materiaux."""
    __tablename__ = "materiaux"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    
    # Relations
    verres = relationship("Verre", back_populates="materiau")

class Gamme(Base):
    """Modèle SQLAlchemy pour la table gammes."""
    __tablename__ = "gammes"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    type = Column(String(50), nullable=False)
    
    # Relations
    verres = relationship("Verre", back_populates="gamme")

class Serie(Base):
    """Modèle SQLAlchemy pour la table series."""
    __tablename__ = "series"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    type = Column(String(50), nullable=False)
    niveau = Column(String(50), nullable=False)
    
    # Relations
    verres = relationship("Verre", back_populates="serie") 