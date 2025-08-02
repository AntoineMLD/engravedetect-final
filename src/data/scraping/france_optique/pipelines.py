import os
import re
import logging
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.api.models.verres import Verre
from src.api.core.database.database import Base
from src.data.processing.cleaner import OpticalDataCleaner
from sqlalchemy import text


class PostgresPipeline:
    def __init__(self):
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.max_retries = 3
        self.retry_delay = 5

        self.items = []

        self.local_image_path = Path(__file__).resolve().parents[4] / "data" / "media" / "gravures"
        self.local_image_path.mkdir(parents=True, exist_ok=True)

    def clean_html_tags(self, text):
        if not text:
            return None
        text = re.sub(r"<br\s*/?>", " ", str(text), flags=re.IGNORECASE)
        return " ".join(BeautifulSoup(text, "html.parser").get_text().split())

    def clean_indice(self, indice_str):
        try:
            clean_str = re.sub(r"[^\d.]", "", str(indice_str))
            return float(clean_str)
        except Exception:
            return None

    def extract_image_url(self, gravure_nasale):
        if not gravure_nasale:
            return None
        if isinstance(gravure_nasale, str) and gravure_nasale.startswith(("http://", "https://")):
            return gravure_nasale
        img_match = re.search(r'src=[\'"]([^\'"]+)[\'"]', str(gravure_nasale))
        if img_match:
            return img_match.group(1)
        if isinstance(gravure_nasale, list):
            return " ".join(str(x) for x in gravure_nasale)
        return str(gravure_nasale)

    def download_image_with_retry(self, image_url, spider):
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                image_name = os.path.basename(image_url)
                local_image_path = self.local_image_path / image_name
                response = requests.get(image_url, stream=True, timeout=30)
                if response.status_code == 200:
                    with open(local_image_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return str(local_image_path)
            except Exception as e:
                spider.logger.error(f"Tentative {retry_count + 1} - erreur téléchargement image : {e}")
                time.sleep(self.retry_delay)
            retry_count += 1
        return None

    def open_spider(self, spider):
        spider.logger.info("🔁 Vidage de la table staging")
        with self.engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE staging"))
            conn.commit()

    def process_item(self, item, spider):
        gravure = item.get("gravure_nasale")

        if isinstance(gravure, list):
            item["gravure_nasale"] = " ".join(gravure)
            item["image_gravure"] = None
        else:
            image_url = self.extract_image_url(gravure)
            if image_url and image_url.startswith(("http", "https")):
                item["image_gravure"] = self.download_image_with_retry(image_url, spider)
                item["gravure_nasale"] = image_url
            else:
                item["gravure_nasale"] = self.clean_html_tags(gravure)

        if "materiaux" in item:
            item["materiaux"] = self.clean_html_tags(item["materiaux"])

        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        spider.logger.info("🔁 Nettoyage des données via OpticalDataCleaner")
        cleaner = OpticalDataCleaner()
        cleaner.insert_raw_data(self.items)
        df_clean = cleaner.clean_dataframe(cleaner.load_data_from_staging())

        session = self.Session()
        try:
            for _, row in df_clean.iterrows():
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
            session.commit()
            spider.logger.info(f"✅ {len(df_clean)} verres insérés dans la base")
        except Exception as e:
            session.rollback()
            spider.logger.error(f"❌ Erreur lors de l'insertion finale : {e}")
        finally:
            session.close()
