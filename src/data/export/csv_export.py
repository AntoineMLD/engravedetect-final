import csv
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def get_connection():
    """Établit une connexion à PostgreSQL."""
    load_dotenv()

    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL must be defined in the .env file")

        engine = create_engine(database_url, pool_pre_ping=True)
        return engine.connect()
    except Exception as error:
        print(f"Erreur de connexion PostgreSQL: {error}")
        raise


def export_staging_to_csv():
    """Exporte toutes les données de la table staging vers un fichier CSV."""

    # Nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"data/staging_export_{timestamp}.csv"

    try:
        # Connexion à la base de données
        print("Connexion à PostgreSQL...")
        with get_connection() as conn:
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

            print("Récupération des données de la table staging...")
            result = conn.execute(text(query))

            # Récupération des noms de colonnes
            columns = result.keys()

            # Récupération de toutes les lignes
            rows = result.fetchall()

            print(f"{len(rows)} lignes récupérées")

            # Écriture dans le fichier CSV
            print(f"Écriture dans le fichier: {csv_filename}")
            with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile, delimiter=";")  # Utilisation du point-virgule pour Excel français

                # Écriture de l'en-tête
                writer.writerow(columns)

                # Écriture des données
                for row in rows:
                    writer.writerow(row)

            print("Export terminé avec succès!")
            print(f"Fichier créé: {csv_filename}")
            print(f"Nombre de lignes exportées: {len(rows)}")

            return csv_filename

    except Exception as e:
        print(f" Erreur lors de l'export: {str(e)}")
        return None


def get_staging_stats():
    """Affiche quelques statistiques sur les données de staging."""
    try:
        with get_connection() as conn:
            # Nombre total de lignes
            result = conn.execute(text("SELECT COUNT(*) FROM staging"))
            total_count = result.fetchone()[0]

            # Nombre de fournisseurs uniques
            result = conn.execute(text("SELECT COUNT(DISTINCT fournisseur) FROM staging"))
            fournisseurs_count = result.fetchone()[0]

            # Nombre de verres par fournisseur
            result = conn.execute(
                text(
                    """
                SELECT fournisseur, COUNT(*) as nb_verres
                FROM staging
                GROUP BY fournisseur
                ORDER BY nb_verres DESC
            """
                )
            )
            fournisseurs_stats = result.fetchall()

            print("\n STATISTIQUES DE LA TABLE STAGING:")
            print(f"Total de verres: {total_count}")
            print(f"Nombre de fournisseurs: {fournisseurs_count}")
            print("\n Répartition par fournisseur:")
            for fournisseur, nb_verres in fournisseurs_stats:
                print(f"   • {fournisseur}: {nb_verres} verres")

    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques: {str(e)}")


def main():
    """Point d'entrée principal du script."""
    print("Export des données staging vers CSV")
    print("=" * 50)

    # Affichage des statistiques
    get_staging_stats()

    print("\n" + "=" * 50)

    # Export vers CSV
    csv_file = export_staging_to_csv()

    if csv_file:
        print("\nExport réussi!")
        print(f"Fichier disponible: {csv_file}")

        # Ouvrir le dossier dans l'explorateur (Windows)
        try:
            os.startfile("data")
        except Exception as e:
            print(f"Impossible d'ouvrir le dossier: {str(e)}")
    else:
        print("\nExport échoué")


if __name__ == "__main__":
    main()
