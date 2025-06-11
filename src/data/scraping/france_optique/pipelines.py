import pyodbc
from itemadapter import ItemAdapter
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

class AzureSQLPipeline:
    """
    Pipeline Scrapy pour enregistrer les données des verres optiques dans Azure SQL Database.
    """

    def __init__(self):
        # Chargement des variables d'environnement
        load_dotenv()
        
        # Récupération des variables d'environnement
        self.server = os.getenv('AZURE_SERVER')
        self.database = os.getenv('AZURE_DATABASE')
        self.username = os.getenv('AZURE_USERNAME')
        self.password = os.getenv('AZURE_PASSWORD')
        
        # Liste des pilotes possibles à essayer
        drivers = [
            '{ODBC Driver 18 for SQL Server}',
            '{ODBC Driver 17 for SQL Server}',
            '{SQL Server}'
        ]
        
        # Essayer chaque pilote jusqu'à ce qu'un fonctionne
        for driver in drivers:
            try:
                self.conn_str = (
                    f'DRIVER={driver};'
                    f'SERVER={self.server};'
                    f'DATABASE={self.database};'
                    f'UID={self.username};'
                    f'PWD={self.password};'
                    'Encrypt=yes;'
                    'TrustServerCertificate=no;'
                    'Connection Timeout=30;'
                )
                # Tester la connexion
                conn = pyodbc.connect(self.conn_str)
                conn.close()
                self.driver = driver
                break
            except pyodbc.Error:
                continue
        else:
            raise Exception("Aucun pilote ODBC SQL Server n'a été trouvé. Veuillez installer le pilote.")
        
        # Initialisation des variables de connexion
        self.conn = None
        self.cursor = None

    def open_spider(self, spider):
        try:
            # Établissement de la connexion
            self.conn = pyodbc.connect(self.conn_str)
            self.cursor = self.conn.cursor()
            
            # Création de la table staging
            self.cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'staging')
                CREATE TABLE staging (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    source_url NVARCHAR(MAX),
                    nom_verre NVARCHAR(MAX),
                    gravure_nasale NVARCHAR(MAX),
                    indice_verre NVARCHAR(MAX),
                    materiaux NVARCHAR(MAX),
                    fournisseur NVARCHAR(MAX)
                )
            ''')
            
            # Création de l'index
            self.cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_staging_id' AND object_id = OBJECT_ID('staging'))
                CREATE INDEX idx_staging_id ON staging (id)
            ''')
            
            # Vider la table staging avant chaque exécution (évite les doublons)
            self.cursor.execute('DELETE FROM staging')
            
            self.conn.commit()
            spider.logger.info("Table staging créée et vidée avec succès")
            
        except Exception as e:
            spider.logger.error(f"Erreur lors de la création de la table : {str(e)}")
            raise

    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)
            
            # Préparation des valeurs avec échappement
            source_url = adapter.get('source_url', '').replace("'", "''")
            nom_verre = adapter.get('nom_verre', '').replace("'", "''")
            gravure_nasale = adapter.get('gravure_nasale', '').replace("'", "''")
            indice_verre = adapter.get('indice_verre', '').replace("'", "''")
            materiaux = adapter.get('materiaux', '').replace("'", "''")
            fournisseur = adapter.get('fournisseur', '').replace("'", "''")
            
            # Utiliser MERGE pour éviter les doublons (basé sur nom_verre + source_url)
            query = f"""
                MERGE staging AS target
                USING (SELECT 
                    '{source_url}' AS source_url,
                    '{nom_verre}' AS nom_verre,
                    '{gravure_nasale}' AS gravure_nasale,
                    '{indice_verre}' AS indice_verre,
                    '{materiaux}' AS materiaux,
                    '{fournisseur}' AS fournisseur
                ) AS source ON (target.nom_verre = source.nom_verre AND target.source_url = source.source_url)
                WHEN NOT MATCHED THEN
                    INSERT (source_url, nom_verre, gravure_nasale, indice_verre, materiaux, fournisseur)
                    VALUES (source.source_url, source.nom_verre, source.gravure_nasale, source.indice_verre, source.materiaux, source.fournisseur)
                WHEN MATCHED THEN
                    UPDATE SET 
                        gravure_nasale = source.gravure_nasale,
                        indice_verre = source.indice_verre,
                        materiaux = source.materiaux,
                        fournisseur = source.fournisseur;
            """
            
            # Exécution directe
            self.cursor.execute(query)
            self.conn.commit()
            
            spider.logger.info(f"✅ Données traitées (MERGE) dans staging : {nom_verre}")
            return item
            
        except Exception as e:
            spider.logger.error(f"❌ Erreur lors de l'insertion des données : {str(e)}")
            self.conn.rollback()
            raise

    def close_spider(self, spider):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            spider.logger.info("Connexion à la base de données fermée avec succès")
        except Exception as e:
            spider.logger.error(f"Erreur lors de la fermeture de la connexion : {str(e)}")

    def test_connection(self):
        """Méthode pour tester la connexion à la base de données"""
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT @@version")
            version = cursor.fetchone()
            print(f"Connexion réussie à Azure SQL Database. Version : {version[0]}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur de connexion : {str(e)}")
            return False
