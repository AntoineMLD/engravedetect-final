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
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f'SERVER={os.getenv("AZURE_SERVER")};'
            f'DATABASE={os.getenv("AZURE_DATABASE")};'
            f'UID={os.getenv("AZURE_USERNAME")};'
            f'PWD={os.getenv("AZURE_PASSWORD")};'
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        # Valeurs par défaut pour le nettoyage
        self.DEFAULT_VALUES = {
            "nom_verre": "Non spécifié",
            "materiaux": "Non spécifié",
            "indice": "1.5",
            "fournisseur": "Non spécifié",
            "gravure_nasale": "Non spécifié",
        }

    def get_connection(self):
        """Retourne une connexion à la base de données Azure SQL."""
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
                    indice,
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
        """Nettoie et prépare le DataFrame pour l'insertion."""
        try:
            # Vérifier que la colonne indice existe
            if "indice" not in df.columns:
                raise ValueError("La colonne 'indice' est manquante dans le DataFrame")

            # Convertir les colonnes en string avant d'appliquer les opérations de nettoyage
            string_columns = ["nom_verre", "materiaux", "fournisseur", "gravure_nasale"]
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            # Nettoyer les colonnes string
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].str.strip()
                    df[col] = df[col].str.replace("\s+", " ", regex=True)

            # Convertir la colonne indice en numérique
            df["indice"] = df["indice"].astype(str).str.replace(",", ".").astype(float)

            # Supprimer les lignes avec des valeurs manquantes essentielles
            df = df.dropna(subset=["nom_verre", "materiaux", "fournisseur"])

            # Supprimer les doublons
            df = df.drop_duplicates()

            # Log du nombre de lignes après nettoyage
            self.logger.info(f"Nombre de lignes après nettoyage : {len(df)}")

            return df

        except Exception as e:
            self.logger.error(f"❌ Erreur lors du nettoyage des données : {e}")
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
                            indice FLOAT,
                            fournisseur NVARCHAR(100),
                            gravure_nasale NVARCHAR(MAX),
                            source_url NVARCHAR(MAX),
                            created_at DATETIME2 DEFAULT GETDATE()
                        )
                    """
                    cursor.execute(create_sql)

                    # Créer les index avec les colonnes de longueur fixe
                    cursor.execute(
                        """
                        CREATE INDEX idx_enhanced_fournisseur ON enhanced (fournisseur)
                    """
                    )
                    cursor.execute(
                        """
                        CREATE INDEX idx_enhanced_materiaux ON enhanced (materiaux)
                    """
                    )

                    conn.commit()
                    self.logger.info("✅ Table enhanced créée avec succès dans Azure SQL")

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la création de la table enhanced : {e}")
            raise

    def export_enhanced_to_csv(self, df: pd.DataFrame) -> str:
        """Exporte les données enhanced vers un fichier CSV."""
        try:
            # Créer le dossier data s'il n'existe pas
            os.makedirs("data", exist_ok=True)

            # Nom du fichier avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"data/enhanced_export_{timestamp}.csv"

            # Export en CSV
            df.to_csv(csv_filename, index=False, sep=";", encoding="utf-8")

            self.logger.info(f"✅ Données exportées vers {csv_filename}")
            return csv_filename

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'export CSV : {e}")
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

            # 3. Export CSV des données nettoyées (staging)
            csv_clean_file = self.export_to_csv(df_clean)

            # 4. Création et insertion dans la table enhanced (optionnel)
            csv_enhanced_file = None
            if create_enhanced_table:
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        # Création de la table enhanced avec contraintes
                        cursor.execute(
                            """
                            IF OBJECT_ID('enhanced', 'U') IS NOT NULL DROP TABLE enhanced;
                            
                            CREATE TABLE enhanced (
                                id INT IDENTITY(1,1) PRIMARY KEY,
                                nom_verre NVARCHAR(MAX) NOT NULL,
                                materiaux NVARCHAR(100) NOT NULL,
                                indice FLOAT,
                                fournisseur NVARCHAR(100) NOT NULL,
                                gravure_nasale NVARCHAR(MAX),
                                source_url NVARCHAR(MAX),
                                created_at DATETIME2 DEFAULT GETDATE()
                            );
                            
                            CREATE INDEX idx_enhanced_fournisseur ON enhanced (fournisseur);
                            CREATE INDEX idx_enhanced_materiaux ON enhanced (materiaux);
                        """
                        )

                        conn.commit()
                        self.logger.info("✅ Table enhanced créée avec succès")

                        # Insertion des données nettoyées
                        self.insert_to_enhanced(df_clean)

                        # Export des données enhanced
                        df_enhanced = self.load_data_from_enhanced()
                        csv_enhanced_file = self.export_enhanced_to_csv(df_enhanced)

            return {"staging_csv": csv_clean_file, "enhanced_csv": csv_enhanced_file}

        except Exception as e:
            self.logger.error(f"❌ Erreur lors du processus de nettoyage et export : {e}")
            raise

    def _prepare_data_for_verres(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les données pour la table verres."""
        try:
            # Copie du DataFrame
            df_prep = df.copy()

            # Vérification que la colonne indice existe
            if "indice" not in df_prep.columns:
                raise ValueError("La colonne 'indice' est manquante dans les données")

            # Renommage des colonnes
            column_mapping = {
                "nom_verre": "nom",
                "materiaux": "materiau",
                "indice": "indice",  # On garde le même nom
                "fournisseur": "fournisseur",
                "gravure_nasale": "gravure",
            }
            df_prep = df_prep.rename(columns=column_mapping)

            # Vérification des colonnes requises après renommage
            required_columns = ["nom", "materiau", "indice", "fournisseur", "gravure"]
            missing_columns = [col for col in required_columns if col not in df_prep.columns]
            if missing_columns:
                raise ValueError(f"Colonnes manquantes après renommage : {', '.join(missing_columns)}")

            # Nettoyage des valeurs d'indice
            df_prep["indice"] = df_prep["indice"].astype(str).str.strip()
            df_prep["indice"] = df_prep["indice"].str.replace(",", ".")

            # Extraction des valeurs numériques
            df_prep["indice"] = df_prep["indice"].str.extract(r"(\d+[.,]?\d*)").iloc[:, 0]

            # Gestion des valeurs manquantes
            missing_before = df_prep["indice"].isna().sum()
            df_prep["indice"] = df_prep["indice"].fillna("1.5")
            self.logger.info(f"⚠️ {missing_before} valeurs d'indice manquantes remplacées par 1.5")

            # Conversion en float et validation des plages
            df_prep["indice"] = pd.to_numeric(df_prep["indice"], errors="coerce").fillna(1.5)

            # Correction des valeurs hors plage
            invalid_before = len(df_prep[df_prep["indice"] < 1.0]) + len(df_prep[df_prep["indice"] > 2.0])
            df_prep.loc[df_prep["indice"] < 1.0, "indice"] = 1.5
            df_prep.loc[df_prep["indice"] > 2.0, "indice"] = 1.5
            self.logger.info(f"⚠️ {invalid_before} valeurs d'indice hors plage corrigées")

            # Arrondi à 2 décimales
            df_prep["indice"] = df_prep["indice"].round(2)

            # Conversion finale en float64
            df_prep["indice"] = df_prep["indice"].astype("float64")

            self.logger.info("✅ Traitement des indices terminé")
            return df_prep

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la préparation des données : {e}")
            raise

    def _handle_references(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gère les références et les clés étrangères."""
        try:
            # Créer d'abord les tables de référence
            self.create_reference_tables()

            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Gestion des fournisseurs
                for fournisseur in df["fournisseur"].unique():
                    if pd.isna(fournisseur):
                        continue

                    # Vérifier si le fournisseur existe
                    cursor.execute(
                        """
                        SELECT id FROM fournisseurs 
                        WHERE nom = ?
                    """,
                        (fournisseur,),
                    )
                    result = cursor.fetchone()

                    if result:
                        fournisseur_id = result[0]
                    else:
                        # Créer le fournisseur
                        cursor.execute(
                            """
                            INSERT INTO fournisseurs (nom)
                            VALUES (?)
                        """,
                            (fournisseur,),
                        )
                        conn.commit()
                        cursor.execute("SELECT @@IDENTITY")
                        fournisseur_id = cursor.fetchone()[0]

                    # Mettre à jour le DataFrame
                    df.loc[df["fournisseur"] == fournisseur, "fournisseur_id"] = fournisseur_id

                # Gestion des matériaux
                for materiau in df["materiaux"].unique():
                    if pd.isna(materiau):
                        continue

                    cursor.execute(
                        """
                        SELECT id FROM materiaux 
                        WHERE nom = ?
                    """,
                        (materiau,),
                    )
                    result = cursor.fetchone()

                    if result:
                        materiau_id = result[0]
                    else:
                        cursor.execute(
                            """
                            INSERT INTO materiaux (nom)
                            VALUES (?)
                        """,
                            (materiau,),
                        )
                        conn.commit()
                        cursor.execute("SELECT @@IDENTITY")
                        materiau_id = cursor.fetchone()[0]

                    df.loc[df["materiaux"] == materiau, "materiau_id"] = materiau_id

            return df

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la gestion des références : {e}")
            raise

    def _clean_specific_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoyage spécifique pour chaque colonne."""

        # Nettoyage des matériaux
        df["materiaux"] = df["materiaux"].str.strip()
        df["materiaux"] = df["materiaux"].str.upper()
        # Standardisation des matériaux
        material_mapping = {
            "ORG": "ORGANIQUE",
            "ORGANIC": "ORGANIQUE",
            "MIN": "MINERAL",
            "MINERAL": "MINERAL",
            "TRIVEX": "TRIVEX",
            "PC": "POLYCARBONATE",
            "POLYCARBONATE": "POLYCARBONATE",
        }
        df["materiaux"] = df["materiaux"].replace(material_mapping)

        # Nettoyage de l'indice (préparation basique)
        if "indice" in df.columns:
            df["indice"] = df["indice"].astype(str).str.strip()
            df["indice"] = df["indice"].replace("", "1.5")  # Valeur par défaut si vide
            df["indice"] = df["indice"].replace("pas d'indice", "1.5")  # Valeur par défaut si pas d'indice

        # Nettoyage du fournisseur
        df["fournisseur"] = df["fournisseur"].str.strip()
        # Supprimer "Produits optiques : " du début si présent
        df["fournisseur"] = df["fournisseur"].str.replace(r"^Produits optiques\s*:\s*", "", regex=True)
        df["fournisseur"] = df["fournisseur"].str.upper()

        # Validation uniquement pour les URLs sources
        df.loc[
            ~df["source_url"].str.startswith(("http://", "https://"), na=False),
            "source_url",
        ] = ""

        return df

    def get_data_statistics(self, df: pd.DataFrame):
        """Affiche les statistiques des données nettoyées."""
        self.logger.info("\n📊 STATISTIQUES DES DONNÉES NETTOYÉES:")
        self.logger.info(f"🔢 Total de verres: {len(df)}")

        # Statistiques par fournisseur
        fournisseurs_stats = df["fournisseur"].value_counts()
        self.logger.info(f"🏢 Nombre de fournisseurs: {len(fournisseurs_stats)}")
        self.logger.info("\n📈 Répartition par fournisseur:")
        for fournisseur, count in fournisseurs_stats.head(10).items():
            self.logger.info(f"   • {fournisseur}: {count} verres")

        # Statistiques par matériau
        materiaux_stats = df["materiaux"].value_counts()
        self.logger.info("\n🔬 Répartition par matériau:")
        for materiau, count in materiaux_stats.items():
            self.logger.info(f"   • {materiau}: {count} verres")

        # Statistiques par indice
        indices_stats = df["indice"].value_counts()
        self.logger.info("\n🔍 Répartition par indice:")
        for indice, count in indices_stats.head(10).items():
            self.logger.info(f"   • {indice}: {count} verres")

    def export_to_csv(self, df: pd.DataFrame) -> str:
        """Exporte le DataFrame nettoyé vers un fichier CSV."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Utiliser le chemin absolu pour le dossier data à la racine
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        data_dir = os.path.join(root_dir, "data")

        # S'assurer que le dossier existe
        if not os.path.exists(data_dir):
            self.logger.error(f"❌ Le dossier data n'existe pas : {data_dir}")
            raise FileNotFoundError(f"Le dossier data n'existe pas : {data_dir}")

        csv_filename = os.path.join(data_dir, f"verres_optiques_clean_{timestamp}.csv")

        try:
            # Export avec encodage UTF-8 et délimiteur point-virgule
            df.to_csv(csv_filename, sep=";", index=False, encoding="utf-8")

            self.logger.info(f"💾 Export CSV terminé: {csv_filename}")
            self.logger.info(f"📊 {len(df)} lignes exportées")

            return csv_filename

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'export CSV : {e}")
            raise

    def insert_to_enhanced(self, df: pd.DataFrame):
        """Insère les données nettoyées dans la table enhanced."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Préparation de la requête d'insertion
                    insert_query = """
                        INSERT INTO enhanced (
                            nom_verre,
                            materiaux,
                            indice,
                            fournisseur,
                            gravure_nasale,
                            source_url
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """

                    # Compteurs pour le suivi
                    total_rows = len(df)
                    inserted_rows = 0
                    error_rows = 0

                    # Insertion ligne par ligne
                    for index, row in df.iterrows():
                        try:
                            # Log des données pour le debug
                            self.logger.debug(f"Insertion ligne {index}:")
                            self.logger.debug(f"nom_verre: {row['nom_verre']}")
                            self.logger.debug(f"materiaux: {row['materiaux']}")
                            self.logger.debug(f"indice: {row['indice']}")
                            self.logger.debug(f"fournisseur: {row['fournisseur']}")
                            self.logger.debug(f"gravure_nasale: {row['gravure_nasale']}")

                            # Exécution de l'insertion
                            cursor.execute(
                                insert_query,
                                (
                                    row["nom_verre"],
                                    row["materiaux"],
                                    row["indice"],
                                    row["fournisseur"],
                                    row["gravure_nasale"],
                                    row["source_url"],
                                ),
                            )
                            inserted_rows += 1

                        except Exception as e:
                            error_rows += 1
                            self.logger.error(f"❌ Erreur lors de l'insertion de la ligne {index}: {e}")
                            self.logger.error(f"Données de la ligne : {row.to_dict()}")

                    conn.commit()

                    # Log du résumé
                    self.logger.info("✅ Résumé de l'insertion:")
                    self.logger.info(f"  - {inserted_rows} lignes insérées avec succès")
                    self.logger.info(f"  - {error_rows} lignes ignorées ou en erreur")

                    # Vérification du nombre final de lignes
                    cursor.execute("SELECT COUNT(*) FROM enhanced")
                    final_count = cursor.fetchone()[0]
                    self.logger.info(f"Nombre final de lignes dans enhanced: {final_count}")

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'insertion dans enhanced : {e}")
            raise

    def load_data_from_enhanced(self):
        """Charge les données depuis la table enhanced."""
        try:
            query = """
                SELECT 
                    id,
                    nom_verre,
                    materiaux,
                    indice,
                    fournisseur,
                    gravure_nasale,
                    source_url
                FROM enhanced 
                ORDER BY id
            """

            with self.get_connection() as conn:
                df = pd.read_sql(query, conn)

            self.logger.info(f"🔍 {len(df)} lignes chargées depuis la table enhanced")
            return df

        except Exception as e:
            self.logger.error(f"❌ Erreur lors du chargement des données enhanced : {e}")
            raise

    def insert_from_enhanced_csv(self, csv_path: str) -> bool:
        """
        Insère les données depuis le CSV enhanced vers la table enhanced avec vérifications.

        Args:
            csv_path: Chemin vers le fichier CSV enhanced

        Returns:
            bool: True si l'insertion a réussi, False sinon
        """
        try:
            self.logger.info(f"📥 Lecture du fichier CSV: {csv_path}")

            # Lecture du CSV
            df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
            self.logger.info(f"📊 {len(df)} lignes lues depuis le CSV")

            # Vérification des colonnes requises
            required_columns = [
                "nom_verre",
                "materiaux",
                "indice",
                "fournisseur",
                "gravure_nasale",
                "source_url",
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.logger.error(f"❌ Colonnes manquantes dans le CSV: {missing_columns}")
                return False

            # Nettoyage des données
            df["nom_verre"] = df["nom_verre"].astype(str).str.strip()
            df["materiaux"] = df["materiaux"].astype(str).str.strip()
            df["fournisseur"] = df["fournisseur"].astype(str).str.strip()
            df["gravure_nasale"] = df["gravure_nasale"].astype(str).str.strip()
            df["source_url"] = df["source_url"].astype(str).str.strip()

            # Conversion de l'indice en float
            df["indice"] = pd.to_numeric(df["indice"], errors="coerce")

            # Vérification des valeurs nulles
            null_counts = df.isnull().sum()
            self.logger.info("Valeurs nulles par colonne:")
            for col, count in null_counts.items():
                self.logger.info(f"  - {col}: {count}")

            # Vérification des valeurs vides
            empty_counts = (df == "").sum()
            self.logger.info("Valeurs vides par colonne:")
            for col, count in empty_counts.items():
                self.logger.info(f"  - {col}: {count}")

            # Insertion dans la table enhanced
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Vérifier que la table est vide
                cursor.execute("SELECT COUNT(*) FROM enhanced")
                count = cursor.fetchone()[0]
                if count > 0:
                    self.logger.warning(f"⚠️ La table enhanced contient déjà {count} lignes")
                    cursor.execute("TRUNCATE TABLE enhanced")
                    self.logger.info("✅ Table enhanced vidée")

                inserted_count = 0
                error_count = 0

                for index, row in df.iterrows():
                    try:
                        # Vérification des valeurs requises
                        if pd.isna(row["nom_verre"]) or pd.isna(row["materiaux"]) or pd.isna(row["fournisseur"]):
                            self.logger.warning(f"⚠️ Ligne {index} ignorée: valeurs requises manquantes")
                            error_count += 1
                            continue

                        # Insertion dans la table enhanced
                        cursor.execute(
                            """
                            INSERT INTO enhanced (
                                nom_verre, materiaux, indice, fournisseur,
                                gravure_nasale, source_url
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                            (
                                row["nom_verre"],
                                row["materiaux"],
                                row["indice"],
                                row["fournisseur"],
                                row["gravure_nasale"],
                                row["source_url"],
                            ),
                        )

                        inserted_count += 1
                        if inserted_count % 100 == 0:
                            self.logger.info(f"✓ {inserted_count} lignes insérées")
                            conn.commit()

                    except Exception as row_error:
                        self.logger.error(f"❌ Erreur lors de l'insertion de la ligne {index}: {str(row_error)}")
                        self.logger.error(f"Données de la ligne : {row.to_dict()}")
                        error_count += 1
                        continue

                conn.commit()
                self.logger.info(f"✅ Résumé de l'insertion:")
                self.logger.info(f"  - {inserted_count} lignes insérées avec succès")
                self.logger.info(f"  - {error_count} lignes ignorées ou en erreur")

                # Vérification finale
                cursor.execute("SELECT COUNT(*) FROM enhanced")
                final_count = cursor.fetchone()[0]
                self.logger.info(f"Nombre final de lignes dans enhanced: {final_count}")

                if final_count == inserted_count:
                    self.logger.info("✅ Vérification réussie: nombre de lignes correspond")
                    return True
                else:
                    self.logger.error(
                        f"❌ Vérification échouée: nombre de lignes incorrect ({final_count} vs {inserted_count})"
                    )
                    return False

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'insertion depuis le CSV : {str(e)}")
            return False

    def insert_to_verres(self, df: pd.DataFrame) -> bool:
        """
        Insère les données dans la table verres à partir des données enhanced.

        Args:
            df: DataFrame contenant les données enhanced

        Returns:
            bool: True si l'insertion a réussi, False sinon
        """
        try:
            self.logger.info("📥 Préparation des données pour la table verres...")

            # Préparer les données pour la table verres
            df_verres = self._prepare_data_for_verres(df)

            # Vérifier que la table est vide
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM verres")
                count = cursor.fetchone()[0]
                if count > 0:
                    self.logger.warning(f"⚠️ La table verres contient déjà {count} lignes")
                    cursor.execute("TRUNCATE TABLE verres")
                    self.logger.info("✅ Table verres vidée")

                inserted_count = 0
                error_count = 0

                for index, row in df_verres.iterrows():
                    try:
                        # Vérification des valeurs requises
                        if pd.isna(row["nom"]) or pd.isna(row["materiau"]) or pd.isna(row["fournisseur"]):
                            self.logger.warning(f"⚠️ Ligne {index} ignorée: valeurs requises manquantes")
                            error_count += 1
                            continue

                        # Insertion dans la table verres
                        cursor.execute(
                            """
                            INSERT INTO verres (
                                nom, materiau, indice, fournisseur, gravure
                            ) VALUES (?, ?, ?, ?, ?)
                        """,
                            (
                                row["nom"],
                                row["materiau"],
                                row["indice"],
                                row["fournisseur"],
                                row["gravure"],
                            ),
                        )

                        inserted_count += 1
                        if inserted_count % 100 == 0:
                            self.logger.info(f"✓ {inserted_count} lignes insérées")
                            conn.commit()

                    except Exception as row_error:
                        self.logger.error(f"❌ Erreur lors de l'insertion de la ligne {index}: {str(row_error)}")
                        self.logger.error(f"Données de la ligne : {row.to_dict()}")
                        error_count += 1
                        continue

                conn.commit()
                self.logger.info(f"✅ Résumé de l'insertion dans verres:")
                self.logger.info(f"  - {inserted_count} lignes insérées avec succès")
                self.logger.info(f"  - {error_count} lignes ignorées ou en erreur")

                # Vérification finale
                cursor.execute("SELECT COUNT(*) FROM verres")
                final_count = cursor.fetchone()[0]
                self.logger.info(f"Nombre final de lignes dans verres: {final_count}")

                return final_count == inserted_count

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'insertion dans verres : {str(e)}")
            return False


def main():
    """Point d'entrée principal du script."""
    cleaner = OpticalDataCleaner()
    cleaner.process_and_export()


if __name__ == "__main__":
    main()
