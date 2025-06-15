# C3. Agrégation des Données

## Contexte
Ce document analyse l'implémentation des scripts d'agrégation et de nettoyage des données dans le projet EngraveDetect. Le projet utilise un pipeline de traitement pour agréger, nettoyer et normaliser les données provenant de différentes sources avant leur stockage final.

## 1. Fonctionnalité du Script d'Agrégation

### 1.1 Pipeline Principal
```python
class DataPipelineManager:
    def clean_and_enhance_data(self) -> bool:
        """
        Nettoie les données et les insère dans la table enhanced.
        
        Returns:
            bool: True si le processus a réussi, False sinon
        """
        try:
            # Charger et nettoyer les données
            df_raw = self.cleaner.load_data_from_staging()
            if df_raw.empty:
                self.logger.error("❌ Aucune donnée à nettoyer dans la table staging")
                return False

            df_clean = self.cleaner.clean_dataframe(df_raw)
            if df_clean.empty:
                self.logger.error("❌ Aucune donnée valide après nettoyage")
                return False

            # Créer la table enhanced et insérer les données
            self.cleaner.create_enhanced_table()
            self.cleaner.insert_to_enhanced(df_clean)

            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du nettoyage des données : {e}")
            return False
```

### 1.2 Nettoyage des Données
```python
class OpticalDataCleaner:
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie et normalise les données du DataFrame.
        
        Args:
            df: DataFrame contenant les données brutes
            
        Returns:
            DataFrame nettoyé et normalisé
        """
        try:
            # Vérification des colonnes requises
            if "indice" not in df.columns:
                raise ValueError("La colonne 'indice' est manquante")

            # Conversion des colonnes en string
            string_columns = ["nom_verre", "materiaux", "fournisseur", "gravure_nasale"]
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str)
                    df[col] = df[col].str.strip()
                    df[col] = df[col].str.replace(r"\s+", " ", regex=True)

            # Normalisation des indices
            df["indice"] = df["indice"].astype(str).str.replace(",", ".").astype(float)

            # Suppression des données corrompues
            df = df.dropna(subset=["nom_verre", "materiaux", "fournisseur"])
            df = df.drop_duplicates()

            return df
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du nettoyage des données : {e}")
            raise
```

### 1.3 Préparation des Données pour le Stockage
```python
def _prepare_data_for_verres(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour la table verres.
    
    Args:
        df: DataFrame contenant les données nettoyées
        
    Returns:
        DataFrame prêt pour l'insertion dans la table verres
    """
    try:
        df_prep = df.copy()
        
        # Renommage des colonnes
        column_mapping = {
            "nom_verre": "nom",
            "materiaux": "materiau",
            "indice": "indice",
            "fournisseur": "fournisseur",
            "gravure_nasale": "gravure",
        }
        df_prep = df_prep.rename(columns=column_mapping)

        # Normalisation des indices
        df_prep["indice"] = df_prep["indice"].astype(str).str.strip()
        df_prep["indice"] = df_prep["indice"].str.replace(",", ".")
        df_prep["indice"] = df_prep["indice"].str.extract(r"(\d+[.,]?\d*)").iloc[:, 0]
        df_prep["indice"] = pd.to_numeric(df_prep["indice"], errors="coerce").fillna(1.5)
        
        # Correction des valeurs hors plage
        df_prep.loc[df_prep["indice"] < 1.0, "indice"] = 1.5
        df_prep.loc[df_prep["indice"] > 2.0, "indice"] = 1.5
        
        # Arrondi et conversion finale
        df_prep["indice"] = df_prep["indice"].round(2).astype("float64")

        return df_prep
    except Exception as e:
        self.logger.error(f"❌ Erreur lors de la préparation des données : {e}")
        raise
```

## 2. Versionnement et Accessibilité

### 2.1 Structure Git
Le script d'agrégation est versionné dans le dépôt Git avec la structure suivante :
```
src/
├── data/
│   ├── processing/
│   │   └── cleaner.py
│   └── scraping/
│       └── france_optique/
│           └── pipelines.py
├── orchestrator/
│   └── pipeline_manager.py
└── scripts/
    └── process_data.py
```

### 2.2 Commandes d'Exécution
```bash
# Activation de l'environnement virtuel
source venv/bin/activate

# Exécution du script de traitement
python src/scripts/process_data.py
```

## 3. Documentation du Script

### 3.1 Dépendances
```python
# Dépendances principales
pandas==2.0.0
numpy==1.24.0
pyodbc==4.0.39
python-dotenv==1.0.0
beautifulsoup4==4.12.0
```

### 3.2 Enchaînements Logiques
1. **Chargement des Données**
   - Lecture depuis la table staging
   - Vérification de la présence des données
   - Conversion en DataFrame pandas

2. **Nettoyage des Données**
   - Suppression des balises HTML
   - Normalisation des formats de texte
   - Conversion des types de données
   - Suppression des doublons

3. **Préparation pour le Stockage**
   - Renommage des colonnes
   - Normalisation des indices
   - Validation des plages de valeurs
   - Conversion finale des types

4. **Insertion dans la Base**
   - Création de la table si nécessaire
   - Insertion des données nettoyées
   - Vérification de l'intégrité

### 3.3 Choix de Nettoyage
1. **Suppression des Données Corrompues**
   ```python
   # Suppression des lignes avec valeurs manquantes essentielles
   df = df.dropna(subset=["nom_verre", "materiaux", "fournisseur"])
   
   # Suppression des doublons
   df = df.drop_duplicates()
   ```

2. **Normalisation des Textes**
   ```python
   # Nettoyage des balises HTML
   def clean_html_tags(self, text):
       if not text:
           return None
       text = re.sub(r"<br\s*/?>", " ", str(text), flags=re.IGNORECASE)
       soup = BeautifulSoup(text, "html.parser")
       return " ".join(soup.get_text().split())
   ```

3. **Normalisation des Indices**
   ```python
   # Conversion et validation des indices
   df["indice"] = df["indice"].astype(str).str.replace(",", ".")
   df["indice"] = pd.to_numeric(df["indice"], errors="coerce").fillna(1.5)
   df.loc[df["indice"] < 1.0, "indice"] = 1.5
   df.loc[df["indice"] > 2.0, "indice"] = 1.5
   ```

### 3.4 Homogénéisation des Formats
1. **Format des Textes**
   - Suppression des espaces multiples
   - Normalisation des caractères spéciaux
   - Conversion en minuscules pour les recherches

2. **Format des Nombres**
   - Conversion des virgules en points
   - Arrondi à 2 décimales
   - Validation des plages de valeurs

## Conclusion

Le script d'agrégation des données du projet EngraveDetect est fonctionnel, versionné et bien documenté. Il implémente un pipeline robuste pour le nettoyage et la normalisation des données, avec une gestion appropriée des erreurs et des logs détaillés.

### Points Forts
1. Pipeline de traitement complet et fonctionnel
2. Gestion robuste des erreurs et des cas limites
3. Documentation détaillée des choix de nettoyage
4. Versionnement clair dans Git
5. Logs détaillés pour le suivi du processus 