# C2. Requêtes SQL d'Extraction des Données — Liste réelle du projet

Ce document liste les requêtes SQL réellement utilisées dans le projet EngraveDetect, vérifiées dans le code source.

---

## 1. Table `staging`

### a) Extraction complète (nettoyage, export, stats)
```sql
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
```
- **Utilisation** : Chargement des données brutes pour nettoyage (`OpticalDataCleaner`).
- **Script** : `src/data/processing/cleaner.py` (méthode `load_data_from_staging`)

### b) Statistiques sur `staging`
```sql
SELECT COUNT(*) FROM staging
SELECT COUNT(DISTINCT fournisseur) FROM staging
SELECT fournisseur, COUNT(*) as nb_verres FROM staging GROUP BY fournisseur ORDER BY nb_verres DESC
```
- **Utilisation** : Statistiques sur le volume et la répartition des données.
- **Script** : `src/data/processing/cleaner.py` (méthode `get_data_statistics`)

---

## 2. Table `enhanced`

### a) Extraction complète (nettoyage, enrichissement, export)
```sql
SELECT
    id,
    nom_verre,
    materiaux,
    indice,
    fournisseur,
    gravure_nasale,
    source_url,
    created_at
FROM enhanced
ORDER BY id
```
- **Utilisation** : Nettoyage, enrichissement, export CSV, migration vers `verres`.
- **Scripts** : `src/data/processing/cleaner.py`, `src/data/processing/enricher.py`

### b) Recherche de valeurs problématiques (corrections)
```sql
SELECT hauteur_max, hauteur_min, fournisseur_id, materiau_id
FROM enhanced
WHERE hauteur_max = 35 OR hauteur_min = 14
   OR fournisseur_id IS NULL OR materiau_id IS NULL
```
- **Utilisation** : Correction des valeurs par défaut et des clés étrangères.
- **Script** : `src/data/processing/fix_enhanced_table.py`

---

## 3. Table `verres`

### a) Extraction complète ou filtrée (API, scripts)
- **Via SQLAlchemy (API)** : Filtres dynamiques sur tous les champs (fournisseur, materiaux, indice, protection, photochromic, etc.)
- **Via SQL direct (scripts)** :
```sql
SELECT
    nom,
    materiaux,
    indice,
    fournisseur,
    gravure
FROM verres
WHERE materiaux = ?
  AND indice BETWEEN ? AND ?
```
- **Utilisation** : Extraction pour l'API, pour analyse, pour export, pour enrichissement.
- **Scripts** : `src/api/services/verres.py`, `src/data/processing/enricher.py`, `src/scripts/extract_tags.py`

### b) Extraction de gravures pour analyse de tags
```sql
SELECT DISTINCT gravure FROM verres WHERE gravure LIKE '%https%'
```
- **Utilisation** : Extraction des gravures contenant des URLs pour analyse de tags.
- **Script** : `src/scripts/extract_tags.py`

### c) Extraction par ID (détail)
```sql
SELECT * FROM verres WHERE id = ?
```
- **Utilisation** : Détail d'un verre (API, IA).
- **Scripts** : `src/api_ia/app/database.py`, API IA `/verre/{id}`

### d) Extraction avec tags non nuls (recherche IA)
```sql
SELECT v.id, v.nom, v.variante, v.hauteur_min, v.hauteur_max,
       v.indice, v.gravure, v.url_source, v.fournisseur, v.tags
FROM verres v
WHERE v.tags IS NOT NULL
```
- **Utilisation** : Recherche IA par tags (API IA).
- **Script** : `src/api_ia/app/database.py`

---

## 4. Table `fournisseurs` et `materiaux` (références)

### a) Extraction des fournisseurs uniques
```sql
SELECT fournisseur, COUNT(*) as nb_verres FROM staging GROUP BY fournisseur
SELECT DISTINCT fournisseur FROM verres
```
- **Utilisation** : Statistiques, filtres API, correction des clés étrangères.
- **Scripts** : `src/data/processing/cleaner.py`, `src/api/services/verres.py`

---

## 5. Table `verres_staging` (rare, migration/correction)

### a) Extraction par ID
```sql
SELECT * FROM verres_staging WHERE id = @verre_id
```
- **Utilisation** : Correction ou migration ponctuelle.
- **Script** : `src/api_ia/app/database.py`

---

## 6. Requêtes de migration

### a) Migration de `enhanced` vers `verres`
```sql
INSERT INTO verres (nom, materiau, indice, fournisseur, gravure_nasale, source_url)
SELECT nom_verre, materiaux, indice, fournisseur, gravure_nasale, source_url
FROM enhanced
```
- **Utilisation** : Migration de données lors de changements de structure.
- **Script** : `src/data/processing/enricher.py` (méthode `process_enhanced_to_verres`)

---

## Explications

- **Toutes les requêtes d'extraction sont utilisées pour le nettoyage, l'enrichissement, l'export, l'analyse, l'API, ou la migration.**
- **Les requêtes sont soit exécutées directement via SQLAlchemy, soit via pandas (API).**
- **Les filtres dynamiques de l'API sont traduits en requêtes SQL par SQLAlchemy.**
- **Les scripts d'export et de stats utilisent des requêtes explicites pour extraire et analyser les données.**
- **Les corrections et migrations utilisent des requêtes ciblées pour garantir l'intégrité des données.**

---



