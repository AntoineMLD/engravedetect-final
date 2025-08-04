"""
Script d'extraction des tags depuis les noms de fichiers

Ce script analyse les noms de fichiers d'images pour extraire
automatiquement les tags de gravures et les sauvegarder en JSON.

Fonctionnalités :
- Analyse récursive des dossiers d'images
- Extraction des tags depuis les noms de fichiers
- Sauvegarde au format JSON structuré
- Gestion des caractères spéciaux et encodage

Auteur : Équipe de développement
Version : 1.0.0
"""

# src/database/extract_tags.py

import json
import os
import re
from pathlib import Path
from typing import List

import psycopg2
from dotenv import load_dotenv


def get_connection():
    """
    Établit une connexion à la base de données PostgreSQL à partir de la variable d'environnement DATABASE_URL.

    Returns:
        connection (psycopg2.extensions.connection): Objet de connexion PostgreSQL.

    Raises:
        Exception: Si la connexion échoue.

    Exemple d'utilisation :
        conn = get_connection()
    """
    load_dotenv()
    try:
        return psycopg2.connect(os.getenv("DATABASE_URL"))
    except Exception as error:
        print(f"Erreur de connexion PostgreSQL : {error}")
        raise


def extract_urls_from_gravure(gravure: str) -> List[str]:
    """
    Extrait toutes les URLs présentes dans une chaîne de caractères de gravure.

    Args:
        gravure (str): Texte contenant potentiellement des URLs.

    Returns:
        List[str]: Liste des URLs extraites.

    Exemple d'utilisation :
        urls = extract_urls_from_gravure("Visitez https://exemple.com #tag")
    """
    if not gravure:
        return []
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    return re.findall(url_pattern, gravure)


def extract_tags_from_gravure(gravure: str) -> List[str]:
    """
    Extrait les tags (hashtags # ou mentions @) d'une chaîne de gravure, en ignorant les URLs.

    Args:
        gravure (str): Texte contenant potentiellement des tags.

    Returns:
        List[str]: Liste des tags extraits, en minuscules et sans doublons.

    Exemple d'utilisation :
        tags = extract_tags_from_gravure("#Optique @Marque https://exemple.com")
    """
    if not gravure:
        return []
    text_without_urls = re.sub(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", "", gravure)
    tags = re.findall(r"[#@]\w+", text_without_urls)
    return list(set(tag.strip("#@").lower() for tag in tags))


def extract_verres_data():
    """
    Extrait les gravures contenant des URLs depuis la base, extrait leurs tags, et génère un fichier JSON.

    Cette fonction :
    - Se connecte à la base PostgreSQL
    - Sélectionne les gravures contenant 'https'
    - Extrait les tags pour chaque gravure
    - Sauvegarde le résultat dans output/verres_tags.json

    Exemple d'utilisation :
        python extract_tags.py
    """
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
            verre_data = {"gravure": gravure, "tags": extract_tags_from_gravure(gravure)}
            verres_data.append(verre_data)

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "verres_tags.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(verres_data, f, ensure_ascii=False, indent=2)

        print(f"Données extraites avec succès dans {output_file}")
        print(f"Nombre de gravures distinctes avec https : {len(verres_data)}")

    except Exception as error:
        print(f"Erreur lors de l'extraction des données : {error}")
        raise
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    extract_verres_data()
