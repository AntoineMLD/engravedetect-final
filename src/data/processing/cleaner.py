import logging
import os
import pandas as pd
import pyodbc
from datetime import datetime
from dotenv import load_dotenv

class OpticalDataCleaner:
    """
    Classe pour nettoyer les données de la table staging Azure SQL et les exporter en CSV.
    """
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Chargement des variables d'environnement
        load_dotenv()
        
        # Configuration de la connexion Azure SQL
        self.conn_str = (
            'DRIVER={ODBC Driver 18 for SQL Server};'
            f'SERVER={os.getenv("AZURE_SERVER")};'
            f'DATABASE={os.getenv("AZURE_DATABASE")};'
            f'UID={os.getenv("AZURE_USERNAME")};'
            f'PWD={os.getenv("AZURE_PASSWORD")};'
            'Encrypt=yes;'
            'TrustServerCertificate=no;'
            'Connection Timeout=30;'
        )
        
        # Valeurs par défaut pour le nettoyage
        self.DEFAULT_VALUES = {
            "nom_verre": "VERRE_INCONNU",
            "materiaux": "ORGANIQUE", 
            "indice_verre": "1.5",
            "fournisseur": "FOURNISSEUR_INCONNU",
            "gravure_nasale": "",
            "source_url": ""
        }

    def get_connection(self):
        """Établit une connexion à Azure SQL."""
        try:
            return pyodbc.connect(self.conn_str)
        except Exception as error:
            self.logger.error(f"❌ Erreur de connexion Azure SQL: {error}")
            raise

    def load_data_from_staging(self):
        """Charge les données depuis la table staging."""
        try:
            query = """
                SELECT 
                    id,
                    source_url,
                    nom_verre,
                    gravure_nasale,
                    indice_verre,
                    materiaux,
                    fournisseur
                FROM staging 
                ORDER BY id
            """
            
            with self.get_connection() as conn:
                df = pd.read_sql(query, conn)
                
            self.logger.info(f"🔍 {len(df)} lignes chargées depuis la table staging")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du chargement des données : {e}")
            raise

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie et standardise le DataFrame."""
        self.logger.info("🧹 Début du nettoyage des données...")
        
        df_clean = df.copy()
        
        # Remplacement des valeurs nulles/vides
        for column, default_value in self.DEFAULT_VALUES.items():
            if column in df_clean.columns:
                # Remplacer les valeurs nulles et les chaînes vides
                df_clean[column] = df_clean[column].fillna(default_value)
                df_clean[column] = df_clean[column].replace('', default_value)
            else:
                df_clean[column] = default_value
        
        # Nettoyage spécifique par colonne
        df_clean = self._clean_specific_columns(df_clean)
        
        # Suppression des doublons
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['nom_verre', 'source_url'], keep='first')
        duplicates_removed = initial_count - len(df_clean)
        
        if duplicates_removed > 0:
            self.logger.info(f"🗑️ {duplicates_removed} doublons supprimés")
        
        self.logger.info(f"✅ Nettoyage terminé. {len(df_clean)} lignes finales")
        return df_clean

    def _clean_specific_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoyage spécifique pour chaque colonne."""
        
        # Nettoyage du nom du verre
        df['nom_verre'] = df['nom_verre'].str.strip()
        df['nom_verre'] = df['nom_verre'].str.upper()
        
        # Nettoyage des matériaux
        df['materiaux'] = df['materiaux'].str.strip()
        df['materiaux'] = df['materiaux'].str.upper()
        # Standardisation des matériaux
        material_mapping = {
            'ORG': 'ORGANIQUE',
            'ORGANIC': 'ORGANIQUE',
            'MIN': 'MINERAL',
            'MINERAL': 'MINERAL',
            'TRIVEX': 'TRIVEX',
            'PC': 'POLYCARBONATE',
            'POLYCARBONATE': 'POLYCARBONATE'
        }
        df['materiaux'] = df['materiaux'].replace(material_mapping)
        
        # Nettoyage de l'indice
        df['indice_verre'] = df['indice_verre'].astype(str).str.strip()
        # Normaliser les indices (ex: "1,67" -> "1.67")
        df['indice_verre'] = df['indice_verre'].str.replace(',', '.')
        
        # Nettoyage du fournisseur
        df['fournisseur'] = df['fournisseur'].str.strip()
        # Supprimer "Produits optiques : " du début si présent
        df['fournisseur'] = df['fournisseur'].str.replace(r'^Produits optiques\s*:\s*', '', regex=True)
        df['fournisseur'] = df['fournisseur'].str.upper()
        
        # Validation uniquement pour les URLs sources
        df.loc[~df['source_url'].str.startswith(('http://', 'https://'), na=False), 'source_url'] = ''
        
        return df

    def get_data_statistics(self, df: pd.DataFrame):
        """Affiche les statistiques des données nettoyées."""
        self.logger.info("\n📊 STATISTIQUES DES DONNÉES NETTOYÉES:")
        self.logger.info(f"🔢 Total de verres: {len(df)}")
        
        # Statistiques par fournisseur
        fournisseurs_stats = df['fournisseur'].value_counts()
        self.logger.info(f"🏢 Nombre de fournisseurs: {len(fournisseurs_stats)}")
        self.logger.info("\n📈 Répartition par fournisseur:")
        for fournisseur, count in fournisseurs_stats.head(10).items():
            self.logger.info(f"   • {fournisseur}: {count} verres")
        
        # Statistiques par matériau
        materiaux_stats = df['materiaux'].value_counts()
        self.logger.info("\n🔬 Répartition par matériau:")
        for materiau, count in materiaux_stats.items():
            self.logger.info(f"   • {materiau}: {count} verres")
        
        # Statistiques par indice
        indices_stats = df['indice_verre'].value_counts()
        self.logger.info("\n🔍 Répartition par indice:")
        for indice, count in indices_stats.head(10).items():
            self.logger.info(f"   • {indice}: {count} verres")

    def export_to_csv(self, df: pd.DataFrame) -> str:
        """Exporte le DataFrame nettoyé vers un fichier CSV."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Utiliser le chemin absolu pour le dossier data à la racine
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        data_dir = os.path.join(root_dir, 'data')
        
        # S'assurer que le dossier existe
        if not os.path.exists(data_dir):
            self.logger.error(f"❌ Le dossier data n'existe pas : {data_dir}")
            raise FileNotFoundError(f"Le dossier data n'existe pas : {data_dir}")
        
        csv_filename = os.path.join(data_dir, f'verres_optiques_clean_{timestamp}.csv')
        
        try:
            # Export avec encodage UTF-8 et délimiteur point-virgule
            df.to_csv(csv_filename, sep=';', index=False, encoding='utf-8')
            
            self.logger.info(f"💾 Export CSV terminé: {csv_filename}")
            self.logger.info(f"📊 {len(df)} lignes exportées")
            
            return csv_filename
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'export CSV : {e}")
            raise

    def create_enhanced_table(self):
        """Crée la table enhanced dans Azure SQL."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Supprimer la table si elle existe
                    cursor.execute("IF OBJECT_ID('enhanced', 'U') IS NOT NULL DROP TABLE enhanced")
                    
                    # Créer la nouvelle table enhanced avec des longueurs fixes pour les colonnes indexées
                    create_sql = """
                        CREATE TABLE enhanced (
                            id INT IDENTITY(1,1) PRIMARY KEY,
                            nom_verre NVARCHAR(MAX),
                            materiaux NVARCHAR(100),
                            indice_verre NVARCHAR(50),
                            fournisseur NVARCHAR(100),
                            gravure_nasale NVARCHAR(MAX),
                            source_url NVARCHAR(MAX),
                            created_at DATETIME2 DEFAULT GETDATE()
                        )
                    """
                    cursor.execute(create_sql)
                    
                    # Créer les index avec les colonnes de longueur fixe
                    cursor.execute("""
                        CREATE INDEX idx_enhanced_fournisseur ON enhanced (fournisseur)
                    """)
                    cursor.execute("""
                        CREATE INDEX idx_enhanced_materiaux ON enhanced (materiaux)
                    """)
                    
                    conn.commit()
                    self.logger.info("✅ Table enhanced créée avec succès dans Azure SQL")
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la création de la table enhanced : {e}")
            raise

    def insert_to_enhanced(self, df: pd.DataFrame):
        """Insère les données nettoyées dans la table enhanced."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    
                    # Préparer la requête d'insertion
                    insert_query = """
                        INSERT INTO enhanced 
                        (nom_verre, materiaux, indice_verre, fournisseur, gravure_nasale, source_url)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    
                    # Insérer ligne par ligne pour éviter les problèmes d'encodage
                    inserted_count = 0
                    for _, row in df.iterrows():
                        cursor.execute(insert_query, (
                            row['nom_verre'],
                            row['materiaux'], 
                            row['indice_verre'],
                            row['fournisseur'],
                            row['gravure_nasale'],
                            row['source_url']
                        ))
                        inserted_count += 1
                    
                    conn.commit()
                    self.logger.info(f"✅ {inserted_count} lignes insérées dans la table enhanced")
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'insertion dans enhanced : {e}")
            raise

    def export_enhanced_to_csv(self, df: pd.DataFrame) -> str:
        """Exporte les données de la table enhanced vers un fichier CSV."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Utiliser le chemin absolu pour le dossier data à la racine
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        data_dir = os.path.join(root_dir, 'data')
        
        # S'assurer que le dossier existe
        if not os.path.exists(data_dir):
            self.logger.error(f"❌ Le dossier data n'existe pas : {data_dir}")
            raise FileNotFoundError(f"Le dossier data n'existe pas : {data_dir}")
        
        csv_filename = os.path.join(data_dir, f'enhanced_export_{timestamp}.csv')
        
        try:
            # Export avec encodage UTF-8 et délimiteur point-virgule
            df.to_csv(csv_filename, sep=';', index=False, encoding='utf-8')
            
            self.logger.info(f"💾 Export CSV enhanced terminé: {csv_filename}")
            self.logger.info(f"📊 {len(df)} lignes exportées depuis enhanced")
            
            return csv_filename
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'export CSV enhanced : {e}")
            raise

    def process_and_export(self, create_enhanced_table=True):
        """Processus complet : charge, nettoie, exporte et optionnellement crée la table enhanced."""
        try:
            self.logger.info("🚀 Début du processus de nettoyage et export")
            self.logger.info("=" * 60)
            
            # 1. Chargement des données
            df_raw = self.load_data_from_staging()
            
            if df_raw.empty:
                self.logger.warning("⚠️ Aucune donnée trouvée dans la table staging.")
                return None
            
            # 2. Nettoyage des données
            df_clean = self.clean_dataframe(df_raw)
            
            # 3. Affichage des statistiques
            self.get_data_statistics(df_clean)
            
            # 4. Export CSV des données nettoyées (staging)
            csv_clean_file = self.export_to_csv(df_clean)
            
            # 5. Création et insertion dans la table enhanced (optionnel)
            csv_enhanced_file = None
            if create_enhanced_table:
                self.logger.info("\n🏗️ Création de la table enhanced...")
                self.create_enhanced_table()
                self.insert_to_enhanced(df_clean)
                
                # 6. Export CSV de la table enhanced
                self.logger.info("\n📤 Export CSV de la table enhanced...")
                csv_enhanced_file = self.export_enhanced_to_csv(df_clean)
            
            self.logger.info("=" * 60)
            self.logger.info(f"✨ Processus terminé avec succès!")
            if create_enhanced_table:
                self.logger.info(f"🗄️ Données insérées dans la table enhanced")
                self.logger.info(f"📁 CSV enhanced: {csv_enhanced_file}")
            self.logger.info(f"📁 CSV nettoyé: {csv_clean_file}")
            
            return {
                'csv_clean': csv_clean_file,
                'csv_enhanced': csv_enhanced_file
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du processus : {e}")
            raise

def main():
    """Point d'entrée principal du script."""
    cleaner = OpticalDataCleaner()
    cleaner.process_and_export()

if __name__ == "__main__":
    main() 