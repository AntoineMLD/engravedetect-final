import subprocess
import os
from datetime import datetime
from sqlalchemy import create_engine, text
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

# Récupération de l'URL de la base PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def count_database_rows():
    """Compte le nombre de lignes dans la table PostgreSQL 'staging'."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM staging"))
            return result.scalar()
    except Exception as error:
        print(f"❌ Erreur PostgreSQL: {error}")
        return 0


def run_spider(spider_name):
    """Exécute un spider Scrapy et affiche le nombre de lignes ajoutées."""
    print(f"\n{'=' * 50}")
    print(f"Spider: {spider_name}")
    print(f"Démarrage: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)

    try:
        initial_count = count_database_rows()

        result = subprocess.run(
            ["scrapy", "crawl", spider_name],
            check=True,
            text=True,
            capture_output=True,
            cwd=os.path.dirname(__file__),
            encoding="utf-8",
        )

        print(result.stdout)

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
