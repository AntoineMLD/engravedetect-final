from sqlalchemy import text
from src.api.core.database.database import Base, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_verres():
    """Réinitialise la table verres."""
    try:
        # Supprimer la table verres si elle existe
        with engine.connect() as conn:
            conn.execute(text("IF OBJECT_ID('verres', 'U') IS NOT NULL DROP TABLE verres"))
            conn.commit()

        # Recréer la table verres
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Table verres réinitialisée avec succès")

    except Exception as e:
        logger.error(f"❌ Erreur lors de la réinitialisation: {str(e)}")
        raise


if __name__ == "__main__":
    reset_verres()
