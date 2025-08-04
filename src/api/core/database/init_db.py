## src/api/core/database/init_db.py
import logging

from sqlalchemy.orm import Session

from ...schemas.auth import UserCreate
from ..auth.service import create_user
from ..config import settings
from .database import Base, SessionLocal, engine

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialise la base de données."""
    logger.info("Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables créées avec succès!")

    # Création de l'utilisateur admin par défaut
    db = SessionLocal()
    try:
        # Création de l'utilisateur admin
        admin_user = UserCreate(email=settings.admin_email, username="admin", password=settings.admin_password)
        create_user(db, admin_user)
        logger.info(f"Utilisateur admin créé avec succès: {settings.admin_email}")
    except Exception as e:
        logger.warning(f"L'utilisateur admin existe déjà ou une erreur est survenue: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
