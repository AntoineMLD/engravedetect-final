# src/database/migrate_to_verres.py

import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.api.core.database.database import SessionLocal, engine
from src.api.models.verres import Verre

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_data():
    """Migre les données de la table enhanced vers la table verres."""
    try:
        with SessionLocal() as session:
            logger.info("Migration des données de enhanced vers verres...")

            # Requête SQL brute (tu peux aussi faire en ORM si tu préfères)
            insert_query = text("""
                INSERT INTO verres (nom, materiau, indice, fournisseur, gravure_nasale, source_url)
                SELECT nom_du_verre, materiaux, indice, fournisseur, gravure_nasale, source_url
                FROM enhanced
            """)

            session.execute(insert_query)
            session.commit()
            logger.info("✅ Données migrées avec succès dans la table verres.")

    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration : {e}")
        raise

if __name__ == "__main__":
    migrate_data()
