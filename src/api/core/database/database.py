from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..config import settings

# Création de l'engine SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Vérifie la connexion avant de l'utiliser
)

# Création de la classe de base pour les modèles
Base = declarative_base()

# Création du SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dépendance pour obtenir une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
