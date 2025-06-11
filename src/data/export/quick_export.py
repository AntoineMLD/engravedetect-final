import pyodbc
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

def quick_export():
    """Export rapide des données staging vers CSV."""
    
    # Connexion
    conn_str = (
        'DRIVER={ODBC Driver 18 for SQL Server};'
        f'SERVER={os.getenv("AZURE_SERVER")};'
        f'DATABASE={os.getenv("AZURE_DATABASE")};'
        f'UID={os.getenv("AZURE_USERNAME")};'
        f'PWD={os.getenv("AZURE_PASSWORD")};'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
    )
    
    # Nom du fichier
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f'data/verres_optiques_{timestamp}.csv'
    
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM staging ORDER BY id")
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(columns)
                writer.writerows(rows)
    
    print(f"✅ Export terminé: {csv_file}")
    print(f"📊 {len(rows)} lignes exportées")

if __name__ == "__main__":
    quick_export() 