import logging
from .database import Base, engine
from ...models import Verre, Fournisseur, Materiau, Gamme, Serie

logger = logging.getLogger(__name__)

def init_db():
    """Initialise la base de données en créant toutes les tables."""
    try:
        logger.info("Création des tables de la base de données...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Base de données initialisée avec succès !")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données : {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db() 