# C3. Agrégation des Données

## Contexte
Ce document décrit l’architecture réelle et le pipeline d’agrégation, de nettoyage, d’enrichissement et d’import des données dans le projet EngraveDetect. Il s’appuie strictement sur les scripts et dépendances présents dans le code.

---

## 1. Vue d’ensemble du pipeline

Le pipeline de données EngraveDetect suit les étapes suivantes :

1. **Scraping** (Scrapy) → insertion en base `staging`
2. **Nettoyage** (`OpticalDataCleaner`) → création de la table `enhanced` et export CSV
3. **Enrichissement** (`DataEnricher`) → ajout de tags, variantes, propriétés, etc.
4. **Corrections post-nettoyage** (`fix_enhanced_table.py`) → gestion des clés étrangères, valeurs par défaut
5. **Import final** (`import_enhanced.py`) → insertion du CSV enhanced en base
6. **Extraction/Insertion de tags** (`extract_tags.py`, `insert_tags.py`)
7. **Orchestration** (`DataPipelineManager`) → exécution séquentielle de toutes les étapes

---

## 2. Scripts et modules principaux

### a) Scraping et pipelines
- **Fichier** : `src/data/scraping/france_optique/pipelines.py`
- **Rôle** : Pipeline Scrapy pour insérer les données brutes dans la table `staging` (Azure SQL), nettoyage HTML, téléchargement d’images.
- **Dépendances** : `pyodbc`, `requests`, `BeautifulSoup`, `sqlalchemy`, `dotenv`, `logging`

### b) Nettoyage et préparation
- **Fichier** : `src/data/processing/cleaner.py`
- **Classe** : `OpticalDataCleaner`
- **Rôle** : Chargement depuis `staging`, nettoyage, création de la table `enhanced`, export CSV, insertion en base, statistiques, gestion des références (fournisseurs, matériaux).
- **Dépendances** : `pandas`, `pyodbc`, `dotenv`, `logging`, `os`, `csv`, `datetime`

### c) Enrichissement
- **Fichier** : `src/data/processing/enricher.py`
- **Classe** : `DataEnricher`
- **Rôle** : Ajout de tags, variantes, détection de propriétés (protection, photochromique), gestion des fournisseurs, etc. Passage de `enhanced` à `verres`.
- **Dépendances** : `pandas`, `sqlalchemy`, `re`, `json`, `logging`

### d) Corrections post-nettoyage
- **Fichier** : `src/data/processing/fix_enhanced_table.py`
- **Rôle** : Corrige les valeurs par défaut, lie les IDs manquants (fournisseur, matériau) dans `enhanced`.
- **Dépendances** : `pyodbc`, `logging`

### e) Import final
- **Fichier** : `src/data/processing/import_enhanced.py`
- **Rôle** : Importe le dernier CSV enhanced en base via `OpticalDataCleaner`.
- **Dépendances** : `logging`, `os`, `pathlib`

### f) Extraction/Insertion de tags
- **Fichiers** : `src/scripts/extract_tags.py`, `src/scripts/insert_tags.py`
- **Rôle** : Extraction des tags des gravures, sauvegarde en JSON, puis insertion en base.
- **Dépendances** : `pyodbc`, `dotenv`, `re`, `json`, `os`, `pathlib`, `logging`

### g) Orchestration
- **Fichier** : `src/orchestrator/pipeline_manager.py`
- **Classe** : `DataPipelineManager`
- **Rôle** : Orchestration du pipeline complet (scraping, nettoyage, enrichissement, corrections, import, etc.).
- **Dépendances** : `logging`, `pathlib`, `scrapy`, `src.data.processing.cleaner`, etc.

---

## 3. Enchaînement logique du pipeline

1. **Lancement du scraping**
   - Exécution des spiders Scrapy (via `DataPipelineManager` ou Scrapy CLI)
   - Insertion des données brutes dans la table `staging`
2. **Nettoyage**
   - Chargement des données de `staging` (`OpticalDataCleaner`)
   - Nettoyage, normalisation, suppression des doublons, gestion des valeurs manquantes
   - Création de la table `enhanced` et insertion des données nettoyées
   - Export CSV des données nettoyées
3. **Enrichissement**
   - Passage de `enhanced` à `verres` via `DataEnricher` (ajout de tags, variantes, propriétés, gestion des clés étrangères)
4. **Corrections post-nettoyage**
   - Script `fix_enhanced_table.py` : correction des valeurs par défaut, liaison des IDs manquants (fournisseur, matériau)
5. **Import final**
   - Script `import_enhanced.py` : import du dernier CSV enhanced en base
6. **Extraction/Insertion de tags**
   - `extract_tags.py` : extraction des tags des gravures, sauvegarde en JSON
   - `insert_tags.py` : insertion des tags extraits dans la base
7. **Orchestration**
   - `DataPipelineManager` : exécution séquentielle de toutes les étapes, gestion des logs et des erreurs

---

## 4. Dépendances Python utilisées

- pandas
- numpy
- pyodbc
- sqlalchemy
- python-dotenv
- beautifulsoup4
- requests
- scrapy
- logging
- os, pathlib, csv, re, json, datetime

---

## 5. Commandes d’exécution principales

```bash
# 1. Lancer le scraping (exemple)
scrapy crawl glass_spider

# 2. Nettoyer et créer la table enhanced
python -m src.data.processing.cleaner

# 3. Enrichir les données
enricher_main()  # ou python -m src.data.processing.enricher

# 4. Corriger la table enhanced
python src/data/processing/fix_enhanced_table.py

# 5. Importer le CSV enhanced en base
python src/data/processing/import_enhanced.py

# 6. Extraire et insérer les tags
python src/scripts/extract_tags.py
python src/scripts/insert_tags.py

# 7. Orchestration complète (optionnel)
python -m src.orchestrator.pipeline_manager
```

---

## 6. Gestion des logs et des erreurs

- Tous les scripts utilisent le module `logging` pour tracer les étapes, erreurs, et statistiques.
- Les erreurs critiques sont loguées et lèvent des exceptions explicites.
- Les scripts de correction et d’import vérifient l’intégrité des données après chaque étape.

---

## 7. Gestion des clés étrangères et corrections post-nettoyage

- Les scripts de correction (`fix_enhanced_table.py`) lient les IDs manquants (fournisseur, matériau) dans la table `enhanced`.
- Les scripts d’enrichissement et d’import vérifient la cohérence des clés étrangères avant insertion dans la table finale `verres`.

---

## Conclusion

Le pipeline d’agrégation de données EngraveDetect est modulaire, robuste, et documenté. Il couvre toutes les étapes : scraping, nettoyage, enrichissement, corrections, import, extraction/insertion de tags, avec gestion des logs et des erreurs à chaque étape. Toutes les dépendances et scripts sont explicitement listés et documentés. 