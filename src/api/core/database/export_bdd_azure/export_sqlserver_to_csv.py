import os
import pandas as pd
from sqlalchemy import create_engine, inspect
import urllib

# Config SQL Server
server = "localhost"
database = "engravedetect"
username = "sa"
password = "Az3rton3359!"
driver = "ODBC Driver 18 for SQL Server"

# Dossier de sortie
output_dir = "/home/scott/Documents/Projets/engravedetect-final/src/api/core/database/export_bdd_azure/csv_exports"

os.makedirs(output_dir, exist_ok=True)

# Connexion SQLAlchemy
params = urllib.parse.quote_plus(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};"
    "Encrypt=Optional;TrustServerCertificate=Yes"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
inspector = inspect(engine)

# Lister les tables
tables = inspector.get_table_names(schema="dbo")
print(f"Tables trouvées dans la base '{database}': {tables}")

# Export CSV par table
for table in tables:
    print(f"Export de la table : {table}")
    df = pd.read_sql_table(table, con=engine, schema="dbo")
    out_path = os.path.join(output_dir, f"{table}.csv")
    df.to_csv(out_path, index=False)
    print(f"✔️ Exportée : {out_path}")

print("Export terminé !")
