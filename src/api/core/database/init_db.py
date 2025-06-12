import logging
from .database import Base, engine

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialise la base de données."""
    logger.info("Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables créées avec succès!")


if __name__ == "__main__":
    init_db()
