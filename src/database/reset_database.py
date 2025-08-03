"""
Script de réinitialisation de la base de données PostgreSQL.

Ce module permet de réinitialiser complètement la base de données en supprimant
et recréant toutes les tables nécessaires au projet de détection de gravures.

Fonctionnalités :
- Suppression sécurisée des tables existantes
- Création des tables staging, enhanced et verres
- Création des index pour optimiser les performances
- Gestion des erreurs et logging détaillé

Tables créées :
- staging : Données brutes en cours de traitement
- enhanced : Données enrichies et nettoyées
- verres : Données finales des verres optiques

Auteur : Équipe de développement
Version : 1.0.0
"""

import logging
from sqlalchemy import create_engine, text
from src.api.core.config import settings  # adapt path if needed

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    try:
        # Créer la connexion PostgreSQL
        engine = create_engine(settings.computed_database_url)

        with engine.connect() as conn:
            logger.info("Suppression des tables existantes (ordre contrôlé)...")

            # Ordre de suppression (respecte les FK si existantes)
            tables_to_drop = ["verres", "enhanced", "staging"]

            for table in tables_to_drop:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                logger.info(f"Table {table} supprimée")

            logger.info("🛠️ Création des tables...")

            # Table staging
            conn.execute(
                text(
                    """
                CREATE TABLE staging (
                    id SERIAL PRIMARY KEY,
                    source_url TEXT,
                    nom_verre TEXT,
                    gravure_nasale TEXT,
                    indice DOUBLE PRECISION,
                    materiaux VARCHAR(100),
                    fournisseur VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Table enhanced
            conn.execute(
                text(
                    """
                CREATE TABLE enhanced (
                    id SERIAL PRIMARY KEY,
                    nom_du_verre TEXT,
                    materiaux VARCHAR(100),
                    indice DOUBLE PRECISION,
                    fournisseur VARCHAR(100),
                    gravure_nasale TEXT,
                    source_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Indexes enhanced
            conn.execute(text("CREATE INDEX idx_enhanced_fournisseur ON enhanced (fournisseur)"))
            conn.execute(text("CREATE INDEX idx_enhanced_materiaux ON enhanced (materiaux)"))

            # Table verres
            conn.execute(
                text(
                    """
                CREATE TABLE verres (
                    id SERIAL PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    materiaux VARCHAR(100),
                    indice DOUBLE PRECISION,
                    fournisseur VARCHAR(100),
                    gravure TEXT,
                    url_source TEXT,
                    variante VARCHAR(100),
                    hauteur_min INTEGER,
                    hauteur_max INTEGER,
                    protection BOOLEAN DEFAULT FALSE,
                    photochromic BOOLEAN DEFAULT FALSE,
                    tags TEXT,
                    image_gravure TEXT
                )
            """
                )
            )

            # Indexes verres
            conn.execute(text("CREATE INDEX idx_verres_nom ON verres (nom)"))
            conn.execute(text("CREATE INDEX idx_verres_fournisseur ON verres (fournisseur)"))
            conn.execute(text("CREATE INDEX idx_verres_materiaux ON verres (materiaux)"))

            conn.commit()
            logger.info("Base de données PostgreSQL réinitialisée avec succès.")

    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation : {e}")


if __name__ == "__main__":
    reset_database()
