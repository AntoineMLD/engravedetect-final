from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from src.api.core.database.database import Base, engine
from src.api.models.verres import Verre
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_data():
    """Migre les données de la table enhanced vers la table verres."""
    try:
        # Créer la table verres si elle n'existe pas
        Base.metadata.create_all(bind=engine)

        # Créer une session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        # Vérifier si la table verres est vide
        count = db.query(Verre).count()
        if count > 0:
            logger.info(f"La table verres contient déjà {count} enregistrements. Suppression...")
            db.query(Verre).delete()
            db.commit()

        # Récupérer les données de la table enhanced
        query = text(
            """
            SELECT 
                nom_verre as nom,
                materiaux,
                indice,
                fournisseur,
                gravure_nasale as gravure,
                source_url as url_source
            FROM enhanced
        """
        )

        result = db.execute(query)
        enhanced_data = result.fetchall()

        # Insérer les données dans la table verres
        for row in enhanced_data:
            verre = Verre(
                nom=row.nom,
                materiaux=row.materiaux,
                indice=row.indice,
                fournisseur=row.fournisseur,
                gravure=row.gravure,
                url_source=row.url_source,
            )
            db.add(verre)

        db.commit()
        logger.info(f"✅ {len(enhanced_data)} verres migrés avec succès")

    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_data()
