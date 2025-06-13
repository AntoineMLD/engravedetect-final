import pyodbc
import logging
import os
from dotenv import load_dotenv
import re
import time
from typing import Dict, List, Set
import requests
from pathlib import Path
from sqlalchemy import create_engine, text
from src.api.core.config import settings
from src.data.processing.cleaner import OpticalDataCleaner
from src.api.models.verres import Verre
from src.api.core.database.database import Base
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup


class AzureSQLPipeline:
    """
    Pipeline Scrapy pour enregistrer les données des verres optiques dans Azure SQL Database.
    """

    def __init__(self):
        # Chargement des variables d'environnement
        load_dotenv()

        # Récupération des variables d'environnement
        self.server = os.getenv("AZURE_SERVER")
        self.database = os.getenv("AZURE_DATABASE")
        self.username = os.getenv("AZURE_USERNAME")
        self.password = os.getenv("AZURE_PASSWORD")

        # Liste des pilotes possibles à essayer
        drivers = [
            "{ODBC Driver 18 for SQL Server}",
            "{ODBC Driver 17 for SQL Server}",
            "{SQL Server}",
        ]

        # Essayer chaque pilote jusqu'à ce qu'un fonctionne
        for driver in drivers:
            try:
                self.conn_str = (
                    f"DRIVER={driver};"
                    f"SERVER={self.server};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                    "Encrypt=yes;"
                    "TrustServerCertificate=no;"
                    "Connection Timeout=30;"
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

        # Dictionnaires et sets pour le suivi
        self.items_by_url: Dict[str, List[dict]] = {}
        self.processed_urls: Set[str] = set()
        self.max_retries = 3
        self.retry_delay = 5

        # Configuration pour la sauvegarde des images
        # Obtenir le chemin absolu du projet
        project_root = Path(__file__).resolve().parents[4]  # Remonte de 4 niveaux depuis le fichier actuel
        self.local_image_path = project_root / "data" / "media" / "gravures"
        self.local_image_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Dossier des images créé : {self.local_image_path}")

        # Initialisation de SQLAlchemy
        self.engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def clean_html_tags(self, text):
        """Nettoie les balises HTML d'un texte."""
        if not text:
            return None
        # Remplacer les balises br par des espaces
        text = re.sub(r"<br\s*/?>", " ", str(text), flags=re.IGNORECASE)
        # Utiliser BeautifulSoup pour nettoyer les autres balises HTML
        soup = BeautifulSoup(text, "html.parser")
        # Nettoyer les espaces multiples et les espaces en début/fin
        return " ".join(soup.get_text().split())

    def clean_indice(self, indice_str):
        """Nettoie et convertit une valeur d'indice en float."""
        if not indice_str:
            return None
        try:
            # Enlever les caractères non numériques sauf le point
            clean_str = re.sub(r"[^\d.]", "", str(indice_str))
            return float(clean_str)
        except (ValueError, TypeError):
            logging.warning(f"Impossible de convertir l'indice: {indice_str}")
            return None

    def extract_image_url(self, gravure_nasale):
        """Extrait l'URL de l'image d'une gravure nasale."""
        if not gravure_nasale:
            return None

        # Si c'est déjà une URL directe
        if isinstance(gravure_nasale, str) and gravure_nasale.startswith(("http://", "https://")):
            return gravure_nasale

        # Si c'est une balise img, extraire le src
        img_match = re.search(r'src=[\'"]([^\'"]+)[\'"]', str(gravure_nasale))
        if img_match:
            return img_match.group(1)

        # Si c'est une liste, joindre en string
        if isinstance(gravure_nasale, list):
            return " ".join(str(x) for x in gravure_nasale)

        return str(gravure_nasale)

    def download_image_with_retry(self, image_url: str, spider) -> str:
        """Télécharge une image avec gestion des retries."""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                image_name = os.path.basename(image_url)
                local_image_path = self.local_image_path / image_name

                response = requests.get(image_url, stream=True, timeout=30)
                if response.status_code == 200:
                    with open(local_image_path, "wb") as out_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            out_file.write(chunk)
                    return str(local_image_path)
                else:
                    retry_count += 1
                    spider.logger.warning(f"Tentative {retry_count}: Image non téléchargée (status {response.status_code})")
                    time.sleep(self.retry_delay)
            except Exception as e:
                retry_count += 1
                spider.logger.error(f"Erreur téléchargement image (tentative {retry_count}): {e}")
                time.sleep(self.retry_delay)

        spider.logger.error(f"Échec téléchargement image après {self.max_retries} tentatives")
        return None

    def open_spider(self, spider):
        """Initialise les ressources à l'ouverture du spider."""
        spider.logger.info(f"Démarrage du pipeline pour: {spider.name}")
        spider.logger.info(f"URLs à traiter: {spider.start_urls}")

        # Initialise un dictionnaire vide pour chaque URL de départ
        for url in spider.start_urls:
            spider.logger.info(f"Initialisation pour URL: {url}")
            self.items_by_url[url] = []

        spider.logger.info(f"État initial items_by_url: {self.items_by_url.keys()}")

        # Vider la table verres au début du scraping
        with self.engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE verres"))
            conn.commit()
            spider.logger.info("Table verres vidée avec succès")

    def process_item(self, item, spider):
        """Traite chaque élément collecté par le spider."""
        try:
            source_url = item["source_url"]
            spider.logger.info(f"Pipeline - Début traitement item pour URL: {source_url}")

            # Vérification et initialisation pour l'URL 644
            if "fournisseur=644" in source_url and source_url not in self.items_by_url:
                spider.logger.warning(f"Forçage initialisation pour URL 644: {source_url}")
                self.items_by_url[source_url] = []

            # Ajoute l'URL aux URLs traitées
            self.processed_urls.add(source_url)

            # Vérifie si l'URL est attendue
            if source_url not in spider.start_urls:
                spider.logger.warning(f"URL non prévue trouvée: {source_url}")

            # Traitement de la gravure nasale
            gravure_nasale = item.get("gravure_nasale")
            if gravure_nasale:
                # Si c'est une liste (cas du texte), on la joint en string
                if isinstance(gravure_nasale, list):
                    item["gravure_nasale"] = " ".join(gravure_nasale)
                    item["image_gravure"] = None  # Pas d'image dans ce cas
                # Si c'est une string et que c'est une URL ou une balise img
                else:
                    image_url = self.extract_image_url(gravure_nasale)
                    if image_url and image_url.startswith(("http", "https")):
                        local_image_path = self.download_image_with_retry(image_url, spider)
                        item["image_gravure"] = local_image_path
                        item["gravure_nasale"] = image_url
                    else:
                        # Nettoyer les balises HTML si c'est du texte
                        item["gravure_nasale"] = self.clean_html_tags(gravure_nasale)

            # Nettoyage des balises HTML dans materiaux
            if "materiaux" in item:
                item["materiaux"] = self.clean_html_tags(item["materiaux"])

            # Ajoute l'item au dictionnaire avec vérification
            if source_url not in self.items_by_url:
                spider.logger.warning(f"Initialisation tardive pour URL: {source_url}")
                self.items_by_url[source_url] = []

            self.items_by_url[source_url].append(dict(item))

            # Insérer dans la table staging
            try:
                with pyodbc.connect(self.conn_str) as conn:
                    cursor = conn.cursor()

                    # Insertion dans staging
                    cursor.execute(
                        """
                        INSERT INTO staging (source_url, nom_verre, gravure_nasale, indice, materiaux, fournisseur)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            item["source_url"],
                            item["nom_verre"],
                            item["gravure_nasale"],
                            item["indice"],
                            item["materiaux"],
                            item["fournisseur"],
                        ),
                    )

                    conn.commit()
                    spider.logger.info(f"Item ajouté à la table staging: {item['nom_verre']}")
            except Exception as e:
                spider.logger.error(f"Erreur lors de l'insertion dans staging: {e}")

            return item

        except Exception as e:
            spider.logger.error(f"Erreur traitement item: {e}")
            raise

    def close_spider(self, spider):
        """Gère le traitement final lors de la fermeture du spider."""
        spider.logger.info("Fermeture pipeline - État final:")
        spider.logger.info(f"URLs traitées: {self.processed_urls}")

        # Nettoyer et charger les données dans verres
        try:
            # Charger les données nettoyées
            cleaner = OpticalDataCleaner()
            df_raw = cleaner.load_data_from_staging()
            df_clean = cleaner.clean_dataframe(df_raw)
            spider.logger.info(f"Données nettoyées chargées: {len(df_clean)} lignes")

            # Réinsérer les données
            session = self.Session()

            try:
                count = 0
                errors = 0
                for _, row in df_clean.iterrows():
                    try:
                        verre = Verre(
                            nom=row["nom_verre"],
                            materiaux=row["materiaux"],
                            indice=self.clean_indice(row["indice"]),
                            fournisseur=row["fournisseur"],
                            gravure=row["gravure_nasale"],
                            url_source=row["source_url"],
                            image_gravure=row.get("image_gravure"),
                        )
                        session.add(verre)
                        count += 1

                        # Commit par lots de 100
                        if count % 100 == 0:
                            session.commit()
                            spider.logger.info(f"Progression: {count} verres insérés")
                    except Exception as e:
                        errors += 1
                        spider.logger.error(f"Erreur lors de l'insertion de la ligne {count}: {e}")
                        session.rollback()
                        continue

                # Commit final
                session.commit()
                spider.logger.info(f"✅ {count} verres insérés avec succès")
                if errors > 0:
                    spider.logger.warning(f"⚠️ {errors} erreurs rencontrées lors de l'insertion")

            except Exception as e:
                session.rollback()
                spider.logger.error(f"Erreur lors de l'insertion: {e}")
                raise
            finally:
                session.close()

        except Exception as e:
            spider.logger.error(f"Erreur lors du processus de nettoyage: {e}")
            raise

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
