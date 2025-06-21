import subprocess
import pyodbc
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Liste des spiders à exécuter
SPIDERS = [
    "glass_spider_hoya",
    "glass_spider_full_xpath",
    "glass_spider",
    "glass_spider_particular",
    "glass_spider_optovision",
    "glass_spider_indo_optical",
]


def get_connection():
    """Établit une connexion à Azure SQL avec le pilote 18."""
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


def count_database_rows():
    """Compte le nombre de lignes dans la table Azure SQL 'staging'."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM staging")
                return cursor.fetchone()[0]
    except Exception as error:
        print(f"❌ Erreur Azure SQL: {error}")
        return 0


def run_spider(spider_name):
    """Exécute un spider Scrapy et affiche le nombre de lignes ajoutées."""
    print(f"\n{'='*50}")
    print(f"Spider: {spider_name}")
    print(f"Démarrage: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)

    try:
        # État initial de la table
        initial_count = count_database_rows()

        # Lancer le spider avec l'encodage correct
        result = subprocess.run(
            ["scrapy", "crawl", spider_name],
            check=True,
            text=True,
            capture_output=True,
            cwd=os.path.dirname(__file__),
            encoding="cp1252",  # Encodage Windows pour les caractères spéciaux
        )

        # Affichage des logs de Scrapy
        print(result.stdout)

        # État final
        final_count = count_database_rows()
        new_items = final_count - initial_count

        print("\nRésultats:")
        print(f"✅ Nouveaux items: {new_items}")
        print(f"📊 Total en base: {final_count}")

    except subprocess.CalledProcessError as error:
        print(f"\n❌ Erreur spider (code {error.returncode}):")
        print(f"STDERR:\n{error.stderr}")
        print(f"STDOUT:\n{error.stdout}")


def main():
    """Point d'entrée du script de scraping."""
    start_time = datetime.now()
    print(f"\n🚀 Démarrage du scraping: {start_time.strftime('%H:%M:%S')}")

    for spider in SPIDERS:
        run_spider(spider)
        print("-" * 50)

    duration = datetime.now() - start_time
    print(f"\n✨ Scraping terminé en {duration.seconds} secondes")


if __name__ == "__main__":
    main()
