import csv
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Chargement des variables d'environnement
load_dotenv()


def quick_export():
    """Export rapide des données staging vers CSV."""

    # Connexion
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL must be defined in the .env file")

    engine = create_engine(database_url, pool_pre_ping=True)

    # Nom du fichier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"data/verres_optiques_{timestamp}.csv"

    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM staging ORDER BY id"))
        columns = result.keys()
        rows = result.fetchall()

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(columns)
            writer.writerows(rows)

    print(f"Export terminé: {csv_file}")
    print(f"{len(rows)} lignes exportées")


if __name__ == "__main__":
    quick_export()
