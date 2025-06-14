import os
import json
import pyodbc
from dotenv import load_dotenv
from typing import List, Dict
import re
from pathlib import Path


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


def extract_urls_from_gravure(gravure: str) -> List[str]:
    """Extrait les URLs d'une chaîne de caractères."""
    if not gravure:
        return []

    # Pattern pour détecter les URLs
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    return re.findall(url_pattern, gravure)


def extract_tags_from_gravure(gravure: str) -> List[str]:
    """Extrait les tags d'une chaîne de caractères."""
    if not gravure:
        return []

    # Supprime les URLs
    text_without_urls = re.sub(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", "", gravure)

    # Extrait les mots qui commencent par # ou @
    tags = re.findall(r"[#@]\w+", text_without_urls)

    # Nettoie les tags (enlève les caractères spéciaux)
    cleaned_tags = [tag.strip("#@").lower() for tag in tags]

    return list(set(cleaned_tags))  # Supprime les doublons


def extract_verres_data():
    """Extrait les données des verres et génère un fichier JSON."""
    try:
        # Connexion à la base de données
        conn = get_connection()
        cursor = conn.cursor()

        # Requête pour extraire les gravures distinctes contenant https
        query = """
        SELECT DISTINCT gravure
        FROM verres
        WHERE gravure LIKE '%https%'
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # Préparation des données
        verres_data = []
        for row in rows:
            gravure = row[0]
            verre_data = {"gravure": gravure, "tags": []}  # Liste de tags vide
            verres_data.append(verre_data)

        # Création du dossier output s'il n'existe pas
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Sauvegarde des données en JSON
        output_file = output_dir / "verres_tags.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(verres_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Données extraites avec succès dans {output_file}")
        print(f"📊 Nombre de gravures distinctes avec https : {len(verres_data)}")

    except Exception as error:
        print(f"❌ Erreur lors de l'extraction des données : {error}")
        raise
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    extract_verres_data()
