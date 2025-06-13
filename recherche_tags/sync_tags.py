import pandas as pd
import ast
from difflib import SequenceMatcher


def clean_text(text):
    if pd.isna(text):
        return ""
    return str(text).lower().strip()


def is_https_link(text):
    if pd.isna(text):
        return False
    text = str(text).lower().strip()
    return text.startswith("http")


def analyze_gravures(df, colonne):
    print(f"\nAnalyse de la colonne {colonne}:")
    print("Premiers exemples de valeurs:")
    print(df[colonne].head(10))
    print("\nTypes de valeurs uniques:")
    print(df[colonne].apply(lambda x: type(x).__name__).value_counts())
    print(
        "\nNombre de valeurs commençant par 'http':",
        df[df[colonne].str.contains("http", na=False, case=False)].shape[0],
    )
    print("\nExemples de valeurs non-http:")
    print(df[~df[colonne].str.contains("http", na=False, case=False)][colonne].head(10))


def similarity_score(str1, str2):
    if pd.isna(str1) or pd.isna(str2):
        return 0
    return SequenceMatcher(None, clean_text(str1), clean_text(str2)).ratio()


def find_best_match(row_azure, df_sqlite):
    scores = []

    for _, row_sqlite in df_sqlite.iterrows():
        score = 0

        # URL exact match (highest weight)
        if clean_text(row_azure["source_url"]) == clean_text(row_sqlite["source_url"]):
            score += 5

        # Gravure nasale match
        if clean_text(row_azure["gravure_nasale"]) == clean_text(row_sqlite["nasal_engraving"]):
            score += 4

        # Indice match
        if clean_text(row_azure["indice"]) == clean_text(row_sqlite["glass_index"]):
            score += 2

        # Nom similarity
        name_score = similarity_score(row_azure["nom_verre"], row_sqlite["glass_name"])
        score += name_score * 3

        # Matériau similarity
        material_score = similarity_score(row_azure["materiaux"], row_sqlite["material"])
        score += material_score * 2

        # Fournisseur similarity
        supplier_score = similarity_score(row_azure["fournisseur"], row_sqlite["glass_supplier_name"])
        score += supplier_score * 1

        scores.append(score)

    if not scores:
        return None, 0

    best_score = max(scores)
    best_index = scores.index(best_score)

    return df_sqlite.iloc[best_index], best_score


def main():
    # Lecture des fichiers CSV
    df_sqlite = pd.read_csv("staging_sqlite.csv")
    df_azure = pd.read_csv("staging_azure.csv")

    print(f"Avant filtrage - SQLite: {len(df_sqlite)} lignes, Azure: {len(df_azure)} lignes")

    # Analyser les colonnes de gravure nasale avant filtrage
    analyze_gravures(df_sqlite, "nasal_engraving")
    analyze_gravures(df_azure, "gravure_nasale")

    # Filtrer pour garder uniquement les lignes avec des liens HTTPS
    df_sqlite = df_sqlite[df_sqlite["nasal_engraving"].apply(is_https_link)]
    df_azure = df_azure[df_azure["gravure_nasale"].apply(is_https_link)]

    print(f"\nAprès filtrage (uniquement liens HTTPS) - SQLite: {len(df_sqlite)} lignes, Azure: {len(df_azure)} lignes")

    # Sauvegarder les versions filtrées
    df_sqlite.to_csv("staging_sqlite_filtered.csv", index=False)
    df_azure.to_csv("staging_azure_filtered.csv", index=False)

    # Conversion des tags en liste Python
    df_sqlite["tags"] = df_sqlite["tags"].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

    # Création des colonnes pour le matching
    df_azure["tags"] = None
    df_azure["match_score"] = 0
    df_azure["matched_glass_name"] = None  # Pour vérification
    df_azure["matched_nasal_engraving"] = None  # Pour vérification

    # Pour chaque ligne dans df_azure, trouver la meilleure correspondance
    for idx, row_azure in df_azure.iterrows():
        best_match, score = find_best_match(row_azure, df_sqlite)

        if best_match is not None and score > 5:  # Seuil minimal de confiance
            df_azure.at[idx, "tags"] = str(best_match["tags"])
            df_azure.at[idx, "match_score"] = score
            df_azure.at[idx, "matched_glass_name"] = best_match["glass_name"]
            df_azure.at[idx, "matched_nasal_engraving"] = best_match["nasal_engraving"]

    # Sélectionner et réorganiser les colonnes pour le fichier final
    columns_order = [
        "id",
        "nom_verre",
        "gravure_nasale",
        "matched_glass_name",
        "matched_nasal_engraving",
        "tags",
        "match_score",
        "indice",
        "materiaux",
        "fournisseur",
        "source_url",
    ]

    # Sauvegarde du résultat
    df_azure[columns_order].to_csv("staging_azure_with_tags.csv", index=False)

    # Affichage des statistiques détaillées
    total_rows = len(df_azure)
    matched_rows = len(df_azure[df_azure["tags"].notna()])
    print(f"\nStatistiques de correspondance :")
    print(f"Total des lignes traitées : {total_rows}")
    print(f"Lignes avec tags trouvés : {matched_rows}")
    print(f"Pourcentage de correspondance : {(matched_rows/total_rows)*100:.2f}%")

    # Afficher quelques exemples de correspondances réussies
    print("\nExemples de correspondances réussies :")
    successful_matches = df_azure[df_azure["tags"].notna()].head(3)
    for _, row in successful_matches.iterrows():
        print(f"\nVerre Azure: {row['nom_verre']}")
        print(f"Gravure nasale: {row['gravure_nasale']}")
        print(f"Correspondance trouvée: {row['matched_glass_name']}")
        print(f"Tags associés: {row['tags']}")
        print(f"Score: {row['match_score']}")


if __name__ == "__main__":
    main()
