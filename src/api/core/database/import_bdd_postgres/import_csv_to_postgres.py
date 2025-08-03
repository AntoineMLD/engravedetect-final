import os

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Config connexion PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:azerton3359@localhost:5432/glass_db"
engine = create_engine(DATABASE_URL)

# Dossier où se trouvent les CSV
CSV_DIR = "/home/scott/Documents/Projets/engravedetect-final/src/api/core/database/export_bdd_azure/csv_exports"

# Exclure les *_prod.csv
csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv") and not f.endswith("_prod.csv")]

# Import CSV → PostgreSQL
print(f"\nConnexion établie à PostgreSQL ({DATABASE_URL})")
print(f"Chargement depuis : {CSV_DIR}\n")

for file in csv_files:
    csv_path = os.path.join(CSV_DIR, file)
    table_name = file.replace(".csv", "")

    try:
        print(f"Import de la table : {table_name}")
        df = pd.read_csv(csv_path)

        if df.empty:
            print(f"Fichier vide : {file} — table non modifiée.")
            continue

        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"Table '{table_name}' mise à jour ({len(df)} lignes)\n")

    except SQLAlchemyError as e:
        print(f"Erreur SQLAlchemy pour '{table_name}': {e}\n")
    except Exception as e:
        print(f"Erreur inattendue pour '{table_name}': {e}\n")

print("Import terminé pour toutes les tables non _prod.")
