import logging
import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import re
import warnings
from typing import Dict, Optional, Any, List

# Suppression de l'avertissement BeautifulSoup pour les URLs
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

class DatabaseConnection:
    """Gestion de la connexion à la base de données."""
    
    def __init__(self):
        load_dotenv()
        self.conn_str = self._build_connection_string()

    def _build_connection_string(self) -> str:
        """Construit la chaîne de connexion à partir des variables d'environnement."""
        return (
            'DRIVER={ODBC Driver 18 for SQL Server};'
            f'SERVER={os.getenv("AZURE_SERVER")};'
            f'DATABASE={os.getenv("AZURE_DATABASE")};'
            f'UID={os.getenv("AZURE_USERNAME")};'
            f'PWD={os.getenv("AZURE_PASSWORD")};'
            'Encrypt=yes;'
            'TrustServerCertificate=no;'
            'Connection Timeout=30;'
        )

    def get_connection(self):
        """Établit une connexion à la base de données."""
        try:
            return pyodbc.connect(self.conn_str)
        except Exception as error:
            logging.error(f"❌ Erreur de connexion à la base de données: {error}")
            raise

class DataCleaner:
    """Nettoyage et extraction des données."""
    
    DEFAULTS = {
        "gamme": "STANDARD",
        "serie": "INCONNU",
        "variante": "STANDARD",
        "hauteur_min": 14,
        "hauteur_max": 14,
        "protection": "NON",
        "photochromic": "NON",
        "materiau": "ORGANIQUE",
        "indice": 1.5,
        "fournisseur": "INCONNU"
    }

    GAMME_MAPPING = {
        "Varilux": "PROGRESSIF_PREMIUM",
        "Eyezen": "UNIFOCAL_DIGITAL"
    }

    SERIE_INFO = {
        "Comfort": {"type": "CONFORT", "niveau": "STANDARD"},
        "XR": {"type": "INNOVATION", "niveau": "HAUT"}
    }

    @staticmethod
    def clean_html(html: str) -> str:
        """Nettoie un champ HTML brut."""
        if not html or pd.isna(html):
            return ""
        try:
            return BeautifulSoup(html, "html.parser").get_text().strip()
        except Exception:
            return ""

    def extract_features_from_name(self, name: str) -> Dict[str, Any]:
        """Analyse le nom du verre pour en extraire les caractéristiques."""
        name = self.clean_html(name)
        serie_info = self._extract_serie(name)
        
        features = {
            "nom": name,
            "gamme": self._extract_gamme(name),
            "serie": serie_info["serie"],
            "serie_type": serie_info["type"],
            "serie_niveau": serie_info["niveau"],
            **self._extract_traitements(name),
            **self._extract_variante_hauteur(name)
        }
        
        return features

    def _extract_gamme(self, name: str) -> str:
        """Extrait la gamme du nom du verre."""
        first_word = name.split(" ")[0]
        return self.GAMME_MAPPING.get(first_word, self.DEFAULTS["gamme"])

    def _extract_serie(self, name: str) -> Dict[str, str]:
        """Extrait la série et ses informations du nom du verre."""
        serie = self.DEFAULTS["serie"]
        serie_type = "STANDARD"
        serie_niveau = "STANDARD"
        
        for known in self.SERIE_INFO:
            if known in name:
                serie = known
                serie_type = self.SERIE_INFO[known]["type"]
                serie_niveau = self.SERIE_INFO[known]["niveau"]
                break
        
        return {
            "serie": serie,
            "type": serie_type,
            "niveau": serie_niveau
        }

    def _extract_traitements(self, name: str) -> Dict[str, str]:
        """Extrait les informations de traitement du nom du verre."""
        return {
            "protection": "OUI" if "Blue" in name or "UV" in name else "NON",
            "photochromic": "OUI" if "Transitions" in name else "NON"
        }

    def _extract_variante_hauteur(self, name: str) -> Dict[str, Any]:
        """Extrait la variante et les hauteurs du nom du verre."""
        is_short = "Short" in name
        return {
            "variante": "COURT" if is_short else self.DEFAULTS["variante"],
            "hauteur_min": 11 if is_short else 14,
            "hauteur_max": 11 if is_short else 14
        }

class TableCreator:
    """Création des tables dans la base de données."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)

    def create_all_tables(self):
        """Crée toutes les tables nécessaires."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Supprimer d'abord toutes les tables dans le bon ordre
                    self._drop_all_tables(cursor)
                    # Créer les tables
                    self._create_reference_tables(cursor)
                    self._create_main_table(cursor)
                    self._create_indexes(cursor)
                    conn.commit()
                    self.logger.info("✅ Tables créées avec succès")
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la création des tables : {e}")
            raise

    def _drop_all_tables(self, cursor):
        """Supprime toutes les tables dans le bon ordre (d'abord les tables avec clés étrangères)."""
        # Supprimer la table principale d'abord
        cursor.execute("IF OBJECT_ID('verres', 'U') IS NOT NULL DROP TABLE verres")
        
        # Puis les tables de référence
        cursor.execute("IF OBJECT_ID('fournisseurs', 'U') IS NOT NULL DROP TABLE fournisseurs")
        cursor.execute("IF OBJECT_ID('materiaux', 'U') IS NOT NULL DROP TABLE materiaux")
        cursor.execute("IF OBJECT_ID('gammes', 'U') IS NOT NULL DROP TABLE gammes")
        cursor.execute("IF OBJECT_ID('series', 'U') IS NOT NULL DROP TABLE series")

    def _create_reference_tables(self, cursor):
        """Crée les tables de référence."""
        self._create_fournisseurs_table(cursor)
        self._create_materiaux_table(cursor)
        self._create_gammes_table(cursor)
        self._create_series_table(cursor)

    def _create_fournisseurs_table(self, cursor):
        cursor.execute("""
            CREATE TABLE fournisseurs (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nom NVARCHAR(100) NOT NULL,
                CONSTRAINT UQ_fournisseur_nom UNIQUE (nom)
            )
        """)

    def _create_materiaux_table(self, cursor):
        cursor.execute("""
            CREATE TABLE materiaux (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nom NVARCHAR(100) NOT NULL,
                CONSTRAINT UQ_materiau_nom UNIQUE (nom)
            )
        """)

    def _create_gammes_table(self, cursor):
        cursor.execute("""
            CREATE TABLE gammes (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nom NVARCHAR(100) NOT NULL,
                type NVARCHAR(50) NOT NULL,
                CONSTRAINT UQ_gamme_nom UNIQUE (nom)
            )
        """)

    def _create_series_table(self, cursor):
        cursor.execute("""
            CREATE TABLE series (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nom NVARCHAR(100) NOT NULL,
                type NVARCHAR(50) NOT NULL,
                niveau NVARCHAR(50) NOT NULL,
                CONSTRAINT UQ_serie_nom UNIQUE (nom)
            )
        """)

    def _create_main_table(self, cursor):
        """Crée la table principale des verres."""
        cursor.execute("""
            CREATE TABLE verres (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nom NVARCHAR(MAX) NOT NULL,
                variante NVARCHAR(50),
                hauteur_min INT,
                hauteur_max INT,
                indice DECIMAL(4,2),
                gravure NVARCHAR(MAX),
                url_source NVARCHAR(500),
                protection BIT DEFAULT 0,
                photochromic BIT DEFAULT 0,
                tags NVARCHAR(MAX),
                fournisseur_id INT,
                materiau_id INT,
                gamme_id INT,
                serie_id INT,
                FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id),
                FOREIGN KEY (materiau_id) REFERENCES materiaux(id),
                FOREIGN KEY (gamme_id) REFERENCES gammes(id),
                FOREIGN KEY (serie_id) REFERENCES series(id)
            )
        """)

    def _create_indexes(self, cursor):
        """Crée les index pour optimiser les performances."""
        # Index sur les clés étrangères
        cursor.execute("CREATE INDEX idx_verres_fournisseur ON verres(fournisseur_id)")
        cursor.execute("CREATE INDEX idx_verres_materiau ON verres(materiau_id)")
        cursor.execute("CREATE INDEX idx_verres_gamme ON verres(gamme_id)")
        cursor.execute("CREATE INDEX idx_verres_serie ON verres(serie_id)")
        
        self.logger.info("✅ Index créés avec succès")

class DataImporter:
    """Import des données dans les tables."""
    
    def __init__(self, db_connection: DatabaseConnection, data_cleaner: DataCleaner):
        self.db = db_connection
        self.cleaner = data_cleaner
        self.logger = logging.getLogger(__name__)

    def import_all_data(self):
        """Importe toutes les données dans les tables."""
        try:
            self._import_reference_data()
            self._import_verres_data()
            self.logger.info("✅ Import des données terminé avec succès")
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'import des données : {e}")
            raise

    def _import_reference_data(self):
        """Importe les données dans les tables de référence."""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                self._import_fournisseurs(cursor)
                self._import_materiaux(cursor)
                self._import_gammes(cursor)
                self._import_series(cursor)
                conn.commit()

    def _import_fournisseurs(self, cursor):
        cursor.execute("""
            INSERT INTO fournisseurs (nom)
            SELECT DISTINCT fournisseur 
            FROM enhanced 
            WHERE fournisseur IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM fournisseurs f 
                WHERE f.nom = enhanced.fournisseur
            )
        """)

    def _import_materiaux(self, cursor):
        cursor.execute("""
            INSERT INTO materiaux (nom)
            SELECT DISTINCT materiaux 
            FROM enhanced 
            WHERE materiaux IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM materiaux m 
                WHERE m.nom = enhanced.materiaux
            )
        """)

    def _import_gammes(self, cursor):
        for nom, type in self.cleaner.GAMME_MAPPING.items():
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM gammes WHERE nom = ?)
                INSERT INTO gammes (nom, type) VALUES (?, ?)
            """, (nom, nom, type))

    def _import_series(self, cursor):
        for nom, info in self.cleaner.SERIE_INFO.items():
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM series WHERE nom = ?)
                INSERT INTO series (nom, type, niveau) VALUES (?, ?, ?)
            """, (nom, nom, info["type"], info["niveau"]))

    def _import_verres_data(self):
        """Importe les données dans la table verres."""
        with self.db.get_connection() as conn:
            df_enhanced = pd.read_sql("SELECT * FROM enhanced", conn)
            
            for _, row in df_enhanced.iterrows():
                self._import_verre(conn, row)
            
            conn.commit()

    def _import_verre(self, conn, row):
        """Importe un verre dans la base de données."""
        features = self.cleaner.extract_features_from_name(row["nom_verre"])
        
        with conn.cursor() as cursor:
            ref_ids = self._get_reference_ids(cursor, row, features)
            self._insert_verre(cursor, row, features, ref_ids)
            
        self.logger.info(f"✅ Verre {row['nom_verre']} importé")

    def _get_reference_ids(self, cursor, row, features) -> Dict[str, Optional[int]]:
        """Récupère les IDs des références pour un verre."""
        return {
            "fournisseur_id": self._get_single_id(cursor, "fournisseurs", "nom", row["fournisseur"]),
            "materiau_id": self._get_single_id(cursor, "materiaux", "nom", row["materiaux"]),
            "gamme_id": self._get_single_id(cursor, "gammes", "nom", features["gamme"]),
            "serie_id": self._get_single_id(cursor, "series", "nom", features["serie"])
        }

    @staticmethod
    def _get_single_id(cursor, table: str, field: str, value: str) -> Optional[int]:
        """Récupère l'ID d'une référence dans une table."""
        if not value:
            return None
        cursor.execute(f"SELECT id FROM {table} WHERE {field} = ?", (value,))
        result = cursor.fetchone()
        return result[0] if result else None

    def _clean_indice(self, indice_str):
        """Nettoie et normalise l'indice du verre."""
        if not indice_str or pd.isna(indice_str):
            return 1.5  # Valeur par défaut
            
        # Convertir en string et nettoyer
        indice = str(indice_str)
        
        # Remplacer la virgule par un point
        indice = indice.replace(",", ".")
        
        # Supprimer tous les caractères non numériques sauf le point
        indice = ''.join(c for c in indice if c.isdigit() or c == '.')
        
        try:
            # Convertir en float
            return float(indice)
        except (ValueError, TypeError):
            self.logger.warning(f"⚠️ Indice invalide '{indice_str}', utilisation de la valeur par défaut 1.5")
            return 1.5

    def _insert_verre(self, cursor, row, features, ref_ids):
        """Insère un verre dans la base de données."""
        try:
            # Préparer la requête d'insertion
            insert_query = """
                INSERT INTO verres (
                    nom,
                    variante,
                    hauteur_min,
                    hauteur_max,
                    indice,
                    gravure,
                    url_source,
                    protection,
                    photochromic,
                    tags,
                    fournisseur_id,
                    materiau_id,
                    gamme_id,
                    serie_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Nettoyer et préparer les valeurs
            indice = self._clean_indice(row["indice_verre"])
            hauteur_min = features.get("hauteur_min", self.cleaner.DEFAULTS["hauteur_min"])
            hauteur_max = features.get("hauteur_max", self.cleaner.DEFAULTS["hauteur_max"])
            
            # Préparer les valeurs pour l'insertion
            values = (
                row["nom_verre"],
                features.get("variante"),
                hauteur_min,
                hauteur_max,
                indice,
                row["gravure_nasale"],
                row["source_url"],
                1 if features.get("protection") == "OUI" else 0,
                1 if features.get("photochromic") == "OUI" else 0,
                None,  # tags (initialement NULL)
                ref_ids.get("fournisseur_id"),
                ref_ids.get("materiau_id"),
                ref_ids.get("gamme_id"),
                ref_ids.get("serie_id")
            )
            
            # Exécuter l'insertion
            cursor.execute(insert_query, values)
            
            self.logger.info(f"✅ Verre {row['nom_verre']} importé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'insertion du verre {row['nom_verre']}: {e}")
            raise

class DatabaseManager:
    """Gestionnaire principal de la base de données."""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.db_connection = DatabaseConnection()
        self.data_cleaner = DataCleaner()
        self.table_creator = TableCreator(self.db_connection)
        self.data_importer = DataImporter(self.db_connection, self.data_cleaner)

    def process(self):
        """Exécute le processus complet de création et import des données."""
        try:
            self.logger.info("🚀 Début du processus")
            self.logger.info("=" * 60)
            
            self.table_creator.create_all_tables()
            self.data_importer.import_all_data()
            
            self.logger.info("=" * 60)
            self.logger.info("✨ Processus terminé avec succès!")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du processus : {e}")
            raise

def main():
    """Point d'entrée principal du script."""
    manager = DatabaseManager()
    manager.process()

if __name__ == "__main__":
    main() 