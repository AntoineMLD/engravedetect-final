from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...core.database.database import Base
from ...core.config import settings


class DatabaseManager:
    """Gestionnaire de base de données pour la création et le remplissage des tables."""

    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Crée toutes les tables dans la base de données."""
        Base.metadata.create_all(bind=self.engine)

    def process(self):
        """Processus principal de création et remplissage des tables."""
        # Créer les tables
        self.create_tables()

        # Ici vous pouvez ajouter la logique pour remplir les tables
        # avec les données de la table enhanced
