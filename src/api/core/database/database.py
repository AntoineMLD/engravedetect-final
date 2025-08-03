# src/api/core/database/database.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event
from ..config import settings
import logging

logger = logging.getLogger(__name__)

# Création de l'engine SQLAlchemy
engine = create_engine(
    settings.computed_database_url,
    pool_pre_ping=True,  # Vérifie la connexion avant de l'utiliser
)

# Création de la classe de base pour les modèles
Base = declarative_base()

# Création du SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Event listeners pour tracer les transactions
@event.listens_for(SessionLocal, "after_begin")
def after_begin(session, transaction, connection):
    logger.info("Transaction BEGIN")


@event.listens_for(SessionLocal, "after_commit")
def after_commit(session):
    logger.info("Transaction COMMIT")


@event.listens_for(SessionLocal, "after_rollback")
def after_rollback(session):
    logger.info("Transaction ROLLBACK")


def get_db():
    """Dépendance pour obtenir une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
