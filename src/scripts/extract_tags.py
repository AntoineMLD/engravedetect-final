# src/database/extract_tags.py

import os
import json
import re
from pathlib import Path
from typing import List

import psycopg2
from dotenv import load_dotenv


def get_connection():
    """Établit une connexion à la base PostgreSQL."""
    load_dotenv()
    try:
        return psycopg2.connect(os.getenv("DATABASE_URL"))
    except Exception as error:
        print(f"❌ Erreur de connexion PostgreSQL : {error}")
        raise


def extract_urls_from_gravure(gravure: str) -> List[str]:
    if not gravure:
        return []
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    return re.findall(url_pattern, gravure)


def extract_tags_from_gravure(gravure: str) -> List[str]:
    if not gravure:
        return []
    text_without_urls = re.sub(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", "", gravure)
    tags = re.findall(r"[#@]\w+", text_without_urls)
    return list(set(tag.strip("#@").lower() for tag in tags))


def extract_verres_data():
    """Extrait les données des verres et génère un fichier JSON."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT gravure
            FROM verres
            WHERE gravure ILIKE '%https%'
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        verres_data = []
        for (gravure,) in rows:
            verre_data = {
                "gravure": gravure,
                "tags": extract_tags_from_gravure(gravure)
            }
            verres_data.append(verre_data)

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "verres_tags.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(verres_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Données extraites avec succès dans {output_file}")
        print(f"📊 Nombre de gravures distinctes avec https : {len(verres_data)}")

    except Exception as error:
        print(f"❌ Erreur lors de l'extraction des données : {error}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    extract_verres_data()
