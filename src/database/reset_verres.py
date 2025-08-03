# src/database/reset_verres.py

from sqlalchemy import text
from src.api.core.database.database import Base, engine
from src.api.models.verres import Verre
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_verres():
    """Réinitialise uniquement la table verres (PostgreSQL)."""
    try:
        with engine.connect() as conn:
            logger.info("Suppression de la table verres si elle existe...")
            conn.execute(text("DROP TABLE IF EXISTS verres CASCADE"))
            conn.commit()

        logger.info("réation de la table verres depuis SQLAlchemy...")
        Base.metadata.create_all(bind=engine, tables=[Verre.__table__])

        logger.info("Table verres réinitialisée avec succès")

    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation : {e}")
        raise


if __name__ == "__main__":
    reset_verres()
