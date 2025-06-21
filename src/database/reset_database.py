import logging
from sqlalchemy import create_engine, text
from ..api.core.config import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """
    Réinitialise complètement la base de données en :
    1. Supprimant toutes les tables existantes
    2. Recréant les tables avec la bonne structure
    3. Créant les index nécessaires
    """
    try:
        # Créer la connexion
        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            # 1. Supprimer toutes les tables existantes
            logger.info("🗑️ Suppression des tables existantes...")

            # Supprimer les tables dans le bon ordre pour éviter les erreurs de contraintes
            tables_to_drop = ["verres", "enhanced", "staging"]

            for table in tables_to_drop:
                conn.execute(text(f"IF OBJECT_ID('{table}', 'U') IS NOT NULL DROP TABLE {table}"))
                logger.info(f"✅ Table {table} supprimée")

            conn.commit()

            # 2. Recréer les tables avec la bonne structure
            logger.info("🏗️ Création des nouvelles tables...")

            # Créer la table staging
            conn.execute(
                text(
                    """
                CREATE TABLE staging (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    source_url NVARCHAR(MAX),
                    nom_verre NVARCHAR(MAX),
                    gravure_nasale NVARCHAR(MAX),
                    indice FLOAT,
                    materiaux NVARCHAR(100),
                    fournisseur NVARCHAR(100),
                    created_at DATETIME2 DEFAULT GETDATE()
                )
            """
                )
            )
            logger.info("✅ Table staging créée")

            # Créer la table enhanced
            conn.execute(
                text(
                    """
                CREATE TABLE enhanced (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nom_verre NVARCHAR(MAX),
                    materiaux NVARCHAR(100),
                    indice FLOAT,
                    fournisseur NVARCHAR(100),
                    gravure_nasale NVARCHAR(MAX),
                    source_url NVARCHAR(MAX),
                    created_at DATETIME2 DEFAULT GETDATE()
                )
            """
                )
            )

            # Créer les index pour enhanced
            conn.execute(
                text(
                    """
                CREATE INDEX idx_enhanced_fournisseur ON enhanced (fournisseur)
            """
                )
            )
            conn.execute(
                text(
                    """
                CREATE INDEX idx_enhanced_materiaux ON enhanced (materiaux)
            """
                )
            )
            logger.info("✅ Table enhanced créée avec ses index")

            # Créer la table verres
            conn.execute(
                text(
                    """
                CREATE TABLE verres (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nom NVARCHAR(255) NOT NULL,
                    materiaux NVARCHAR(100),
                    indice FLOAT,
                    fournisseur NVARCHAR(100),
                    gravure NVARCHAR(MAX),
                    url_source NVARCHAR(MAX),
                    variante NVARCHAR(100),
                    hauteur_min INT,
                    hauteur_max INT,
                    protection BIT DEFAULT 0,
                    photochromic BIT DEFAULT 0,
                    tags NVARCHAR(MAX),
                    image_gravure NVARCHAR(MAX)
                )
            """
                )
            )

            # Créer les index pour verres
            conn.execute(
                text(
                    """
                CREATE INDEX idx_verres_nom ON verres (nom)
            """
                )
            )
            conn.execute(
                text(
                    """
                CREATE INDEX idx_verres_fournisseur ON verres (fournisseur)
            """
                )
            )
            conn.execute(
                text(
                    """
                CREATE INDEX idx_verres_materiaux ON verres (materiaux)
            """
                )
            )
            logger.info("✅ Table verres créée avec ses index")

            conn.commit()

            logger.info("✨ Base de données réinitialisée avec succès!")
            return True

    except Exception as e:
        logger.error(f"❌ Erreur lors de la réinitialisation de la base de données : {e}")
        return False


if __name__ == "__main__":
    reset_database()
