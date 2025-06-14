import os
from dotenv import load_dotenv
import pyodbc
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from src.api.core.database.database import Base, engine
from src.api.models.verres import Verre
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    """Établit une connexion à Azure SQL."""
    load_dotenv()
    try:
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f'SERVER={os.getenv("AZURE_SERVER")};'
            f'DATABASE={os.getenv("AZURE_DATABASE")};'
            f'UID={os.getenv("AZURE_USERNAME")};'
            f'PWD={os.getenv("AZURE_PASSWORD")};'
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        return pyodbc.connect(conn_str)
    except Exception as error:
        print(f"❌ Erreur de connexion Azure SQL: {error}")
        raise


def migrate_data():
    """Migre les données de la table enhanced vers la table verres."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Vérifier que la table verres existe
                cursor.execute(
                    """
                    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'verres')
                    BEGIN
                        CREATE TABLE verres (
                            id INT IDENTITY(1,1) PRIMARY KEY,
                            nom NVARCHAR(MAX) NOT NULL,
                            materiau NVARCHAR(100) NOT NULL,
                            indice FLOAT,
                            fournisseur NVARCHAR(100) NOT NULL,
                            gravure_nasale NVARCHAR(MAX),
                            source_url NVARCHAR(MAX),
                            created_at DATETIME2 DEFAULT GETDATE()
                        )
                    END
                """
                )
                conn.commit()
                print("✅ Table verres créée ou déjà existante")

                # Migrer les données
                cursor.execute(
                    """
                    INSERT INTO verres (nom, materiau, indice, fournisseur, gravure_nasale, source_url)
                    SELECT nom_verre, materiaux, indice, fournisseur, gravure_nasale, source_url
                    FROM enhanced
                """
                )
                conn.commit()
                print("✅ Données migrées avec succès")

    except Exception as e:
        print(f"❌ Erreur lors de la migration : {e}")
        raise


if __name__ == "__main__":
    migrate_data()
