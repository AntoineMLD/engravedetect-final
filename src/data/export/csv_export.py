import pyodbc
import csv
import os
from datetime import datetime
from dotenv import load_dotenv


def get_connection():
    """Établit une connexion à Azure SQL avec le pilote 18."""
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


def export_staging_to_csv():
    """Exporte toutes les données de la table staging vers un fichier CSV."""

    # Nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"data/staging_export_{timestamp}.csv"

    try:
        # Connexion à la base de données
        print("🔗 Connexion à Azure SQL...")
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Requête pour récupérer toutes les données
                query = """
                SELECT
                    id,
                    source_url,
                    nom_verre,
                    gravure_nasale,
                    indice,
                    materiaux,
                    fournisseur
                FROM staging
                ORDER BY id
                """

                print("📊 Récupération des données de la table staging...")
                cursor.execute(query)

                # Récupération des noms de colonnes
                columns = [column[0] for column in cursor.description]

                # Récupération de toutes les lignes
                rows = cursor.fetchall()

                print(f"✅ {len(rows)} lignes récupérées")

                # Écriture dans le fichier CSV
                print(f"💾 Écriture dans le fichier: {csv_filename}")
                with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile, delimiter=";")  # Utilisation du point-virgule pour Excel français

                    # Écriture de l'en-tête
                    writer.writerow(columns)

                    # Écriture des données
                    for row in rows:
                        writer.writerow(row)

                print("🎉 Export terminé avec succès!")
                print(f"📁 Fichier créé: {csv_filename}")
                print(f"📈 Nombre de lignes exportées: {len(rows)}")

                return csv_filename

    except Exception as e:
        print(f"❌ Erreur lors de l'export: {str(e)}")
        return None


def get_staging_stats():
    """Affiche quelques statistiques sur les données de staging."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Nombre total de lignes
                cursor.execute("SELECT COUNT(*) FROM staging")
                total_count = cursor.fetchone()[0]

                # Nombre de fournisseurs uniques
                cursor.execute("SELECT COUNT(DISTINCT fournisseur) FROM staging")
                fournisseurs_count = cursor.fetchone()[0]

                # Nombre de verres par fournisseur
                cursor.execute(
                    """
                    SELECT fournisseur, COUNT(*) as nb_verres
                    FROM staging
                    GROUP BY fournisseur
                    ORDER BY nb_verres DESC
                    """
                )
                fournisseurs_stats = cursor.fetchall()

                print("\n📊 STATISTIQUES DE LA TABLE STAGING:")
                print(f"🔢 Total de verres: {total_count}")
                print(f"🏢 Nombre de fournisseurs: {fournisseurs_count}")
                print("\n📈 Répartition par fournisseur:")
                for fournisseur, nb_verres in fournisseurs_stats:
                    print(f"   • {fournisseur}: {nb_verres} verres")

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques: {str(e)}")


def main():
    """Point d'entrée principal du script."""
    print("🚀 Export des données staging vers CSV")
    print("=" * 50)

    # Affichage des statistiques
    get_staging_stats()

    print("\n" + "=" * 50)

    # Export vers CSV
    csv_file = export_staging_to_csv()

    if csv_file:
        print("\n✨ Export réussi!")
        print(f"📁 Fichier disponible: {csv_file}")

        # Ouvrir le dossier dans l'explorateur (Windows)
        try:
            os.startfile("data")
        except Exception as e:
            print(f"❌ Impossible d'ouvrir le dossier: {str(e)}")
    else:
        print("\n❌ Export échoué")


if __name__ == "__main__":
    main()
