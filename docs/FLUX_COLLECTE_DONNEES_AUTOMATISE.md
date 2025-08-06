# Flux Automatisé de Collecte des Données - EngraveDetect

## Présentation du Projet et Contexte

### Contexte et Acteurs

**EngraveDetect** est un projet de développement d'outil numérique pour les opticiens, visant à faciliter la recherche d'informations techniques des verres optiques par identification de la gravure sur le verre progressif.

#### **Acteurs du Projet**
- **Développeur principal** : Antoine (auteur du projet)
- **Partie prenante métier** : Opticien professionnel (expertise technique)
- **Utilisateurs finaux** : Opticiens en activité
- **Équipe de développement** : Développement en autonomie complète

#### **Partenaires et Fournisseurs**
- **Aucun partenaire technique** externe
- **Aucun fournisseur** de services tiers
- **Approche open source** : Utilisation exclusive de technologies libres

### Objectifs Fonctionnels

#### **Besoin Métier Principal**
Permettre aux opticiens de **gagner du temps** en disposant d'un outil numérique pour faciliter la recherche d'informations techniques des verres optiques par identification de la gravure sur le verre progressif.

#### **Processus Opérationnel Ciblé**
1. **Saisie d'image** : L'opticien photographie la gravure sur le verre
2. **Analyse automatique** : Le système identifie le type de gravure
3. **Recherche d'informations** : Récupération des données techniques associées
4. **Affichage des résultats** : Présentation des caractéristiques du verre

#### **Indicateurs de Performance (KPIs)**
- **Temps de réponse** : Obtention des informations du verre en **moins de 3 minutes**
- **Précision de classification** : **Plus de 70%** de précision dans l'identification

### Objectifs Techniques

#### **Critères de Performance**
- **Temps de réponse** : Rapide (optimisation pour usage en magasin)
- **Précision** : Plus de 70% de précision dans la classification des gravures
- **Disponibilité** : Service accessible 24/7 pour les opticiens

#### **Contraintes Techniques**
- **Sécurité RGPD** : Conformité standard aux normes de protection des données
- **Autonomie technique** : Développement et maintenance en autonomie complète
- **Open source** : Utilisation exclusive de technologies libres

### Environnements et Contraintes Techniques

#### **Environnement de Développement**
- **Système d'exploitation** : Linux
- **Technologies** : Bibliothèques listées dans le repository du projet
- **Développement** : Environnement local avec Docker

#### **Environnement de Production**
- **Hébergement** : Serveur VPS via Coolify
- **Domaine** : engravedetect.fr
- **Architecture** : Conteneurisation Docker complète
- **Gestion** : Déploiement automatisé via Coolify

#### **Contraintes Techniques**
- **Infrastructure** : Serveur VPS unique (pas de cloud distribué)
- **Performance** : Optimisation pour usage en magasin d'optique
- **Sécurité** : Authentification et autorisation des utilisateurs

### Budget et Contraintes Économiques

#### **Stratégie Budgétaire**
- **Approche open source** : Choix de l'autonomie technique
- **Pas de services cloud** : Évitement des coûts récurrents élevés
- **Hébergement minimal** : Serveur VPS à 4,50€ par mois

#### **Répartition des Coûts**
- **Infrastructure** : 4,50€/mois (serveur VPS)
- **Développement** : Coût en temps de développement (autonomie)
- **Maintenance** : Gestion en autonomie (pas de coûts externes)

#### **Contraintes Budgétaires**
- **Minimisation des coûts** : Utilisation exclusive de technologies gratuites
- **Autonomie technique** : Évitement des dépendances payantes
- **Gestion Docker** : Conteneurisation pour optimiser les ressources

### Organisation du Travail

#### **Méthodologie**
- **Framework** : Scrum Agile adapté
- **Participation** : Travail en collaboration avec la partie prenante (opticien)
- **Adaptation** : Scrum events ajustés pour le travail en solo

#### **Rôles et Responsabilités**
- **Product Owner** : Antoine (développeur principal)
- **Scrum Master** : Antoine (auto-gestion)
- **Développeur** : Antoine (développement complet)
- **Partie prenante** : Opticien professionnel (validation métier)

#### **Événements Scrum Adaptés**
- **Sprint Planning** : Planification en autonomie avec validation partie prenante
- **Daily Standup** : Auto-évaluation quotidienne
- **Sprint Review** : Démonstration à la partie prenante
- **Sprint Retrospective** : Auto-évaluation et amélioration continue

### Planification et Jalons

#### **Durée du Projet**
- **Début** : Novembre 2024
- **Fin prévue** : Juin 2025
- **Durée totale** : 8 mois

#### **Sprints**
- **Durée des sprints** : 15 jours
- **Nombre de sprints** : 16 sprints au total
- **Rythme** : 2 sprints par mois

#### **Jalons Principaux**
- **Novembre 2024** : Lancement du projet
- **Décembre 2024** : Première version fonctionnelle
- **Mars 2025** : Version beta avec classification
- **Mai 2025** : Version finale et tests
- **Juin 2025** : Mise en production et formation

#### **Livrables par Phase**
- **Phase 1** (Nov-Déc 2024) : Architecture et collecte de données
- **Phase 2** (Jan-Fév 2025) : Développement du modèle IA
- **Phase 3** (Mar-Avr 2025) : Interface utilisateur et API
- **Phase 4** (Mai-Juin 2025) : Tests, optimisation et déploiement

---

## Vue d'ensemble

Ce document présente le flux automatisé de collecte des données mis en place dans le projet EngraveDetect. Ce système permet l'extraction, le traitement et l'intégration automatique des données de gravures optiques depuis diverses sources vers la base de données du projet.

---

## 1. Architecture du Flux de Données

### 1.1 Composants Principaux

Le flux automatisé repose sur plusieurs composants interconnectés :

- **Orchestrateur** : `src/orchestrator/pipeline_manager.py`
- **Extracteurs de données** : Spiders Scrapy dans `src/data/scraping/`
- **Processeurs** : Modules de nettoyage et enrichissement dans `src/data/processing/`
- **Scripts utilitaires** : Outils d'extraction et d'insertion dans `src/scripts/`
- **Gestionnaires de datasets** : Outils de division et préparation dans `src/datasets/`

### 1.2 Flux de Données

```
Sources Web → Spiders Scrapy → Base Staging → Nettoyage → Enrichissement → Base Production
     ↓              ↓              ↓            ↓            ↓              ↓
  france-optique  Extraction   PostgreSQL   Cleaner    Enricher    Verres Final
  autres sites    Images       Table Staging  Enhanced   Tags       API Access
```

---

## 2. Extraction Automatisée des Données

### 2.1 Sources de Données Automatisées

Le système EngraveDetect automatise l'extraction de données depuis plusieurs types de sources :

#### a) Services Web et Pages Web (Scraping)
- **Sites web d'optique** : Extraction depuis france-optique.com
- **APIs publiques** : Intégration de services web d'optique
- **Pages dynamiques** : Gestion du JavaScript et contenu dynamique

#### b) Fichiers de Données
- **Images de gravures** : Traitement automatique des fichiers JPG/PNG
- **CSV d'import** : Chargement de données structurées
- **Fichiers de configuration** : Paramètres et métadonnées

#### c) Base de Données
- **PostgreSQL** : Extraction depuis tables staging, enhanced, verres
- **Synchronisation** : Mise à jour automatique entre tables
- **Export/Import** : Transferts automatisés de données

### 2.2 Spiders Scrapy

**Fichier principal** : `src/data/scraping/france_optique/spiders/glass_spider.py`

Les spiders Scrapy effectuent l'extraction automatique des données depuis les sites web d'optique :

```python
class GlassSpider(scrapy.Spider):
    name = "glass_spider"
    allowed_domains = ["www.france-optique.com"]
    start_urls = [
        "https://www.france-optique.com/fournisseur/1344-bbgr-optique/gravures",
        "https://www.france-optique.com/fournisseur/2399-adn-optis",
    ]
```

**Fonctionnalités** :
- Extraction des données de verres optiques (nom, gravure nasale, indice, matériaux, fournisseur)
- Parsing HTML avec XPath et CSS
- Création d'items structurés FranceOptiqueItem
- Gestion des erreurs et logging

**Spiders disponibles** :
- `glass_spider.py` : Spider principal
- `glass_spider_hoya.py` : Spider spécialisé Hoya
- `glass_spider_optovision.py` : Spider Optovision
- `glass_spider_particular.py` : Spider particularités
- `glass_spider_indo_optical.py` : Spider Indo Optical
- `glass_spider_full_xpath.py` : Spider avec XPath complet

### 2.3 Pipeline de Traitement Scrapy

**Fichier** : `src/data/scraping/france_optique/pipelines.py`

Le pipeline PostgresPipeline assure :
- Nettoyage HTML des données extraites
- Insertion automatique en base de données staging
- Gestion des erreurs et logging

### 2.4 Automatisation des Fichiers de Données

**Scripts de traitement** :
- **Images** : Traitement automatique des gravures dans `data/`
- **CSV** : Import/export automatisé via `OpticalDataCleaner`
- **Datasets** : Division automatique avec `split_dataset.py`

### 2.5 Automatisation Base de Données

**Fichiers** : `src/data/processing/cleaner.py`, `src/data/processing/enricher.py`

**Fonctionnalités** :
- **Extraction** : Chargement automatique depuis table staging
- **Transformation** : Nettoyage et enrichissement automatisé
- **Chargement** : Insertion automatique vers tables enhanced et verres
- **Synchronisation** : Mise à jour automatique entre tables

### 2.6 Développement de Requêtes SQL d'Extraction

**Fichiers** : `src/data/processing/cleaner.py`, `src/data/export/csv_export.py`, `src/api_ia/app/database.py`

Le projet développe des requêtes SQL spécifiques pour l'extraction des données depuis PostgreSQL :

#### a) Requêtes d'Extraction de Données Brutes

**Extraction depuis la table staging** :
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

**Extraction depuis la table enhanced** :
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

#### b) Requêtes d'Analyse et Statistiques

**Statistiques de la table staging** :
```sql
-- Nombre total de verres
SELECT COUNT(*) FROM staging

-- Nombre de fournisseurs uniques
SELECT COUNT(DISTINCT fournisseur) FROM staging

-- Répartition par fournisseur
SELECT fournisseur, COUNT(*) as nb_verres
FROM staging
GROUP BY fournisseur
ORDER BY nb_verres DESC
```

#### c) Requêtes de Recherche Intelligente

**Recherche de verres par tags** :
```sql
-- Recherche avec logique intelligente (Top 20 + tags manuels)
SELECT * FROM verres 
WHERE tags @> '["cercle", "marque"]'::jsonb
```

**Recherche par fournisseur et matériau** :
```sql
SELECT nom, materiau, indice, fournisseur, gravure
FROM verres
WHERE fournisseur = :fournisseur AND materiau = :materiau
```

#### d) Requêtes de Gestion des Références

**Extraction des fournisseurs** :
```sql
SELECT id FROM fournisseurs
```

**Extraction des matériaux** :
```sql
SELECT id FROM materiaux
```

#### e) Requêtes d'Insertion et Mise à Jour

**Insertion dans la table enhanced** :
```sql
INSERT INTO enhanced (
    nom_verre, materiaux, indice, fournisseur, 
    gravure_nasale, source_url
) VALUES (:nom_verre, :materiaux, :indice, :fournisseur, 
          :gravure_nasale, :source_url)
```

**Insertion dans la table verres** :
```sql
INSERT INTO verres (
    nom, materiau, indice, fournisseur, gravure
) VALUES (:nom, :materiau, :indice, :fournisseur, :gravure)
```

#### f) Fonctionnalités SQL Avancées

**Utilisation de SQLAlchemy** :
- Requêtes paramétrées avec `text()` pour la sécurité
- Gestion des connexions avec context managers
- Transactions automatiques avec commit/rollback

**Optimisations** :
- Index sur les colonnes fréquemment utilisées
- Requêtes préparées pour les insertions répétées
- Gestion des erreurs et logging SQL

### 2.7 Catalogue Complet des Requêtes SQL du Projet

#### **A. Requêtes de Création de Tables et Index**

**Fichier** : `src/database/reset_database.py`

**Création de la table staging** :
```sql
CREATE TABLE staging (
    id SERIAL PRIMARY KEY,
    source_url TEXT,
    nom_verre TEXT,
    gravure_nasale TEXT,
    indice DOUBLE PRECISION,
    materiaux VARCHAR(100),
    fournisseur VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
**Fonction** : Table de stockage des données brutes extraites par scraping

**Création de la table enhanced** :
```sql
CREATE TABLE enhanced (
    id SERIAL PRIMARY KEY,
    nom_du_verre TEXT,
    materiaux VARCHAR(100),
    indice DOUBLE PRECISION,
    fournisseur VARCHAR(100),
    gravure_nasale TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
**Fonction** : Table de données nettoyées et enrichies

**Création de la table verres** :
```sql
CREATE TABLE verres (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    materiaux VARCHAR(100),
    indice DOUBLE PRECISION,
    fournisseur VARCHAR(100),
    gravure TEXT,
    url_source TEXT,
    variante VARCHAR(100),
    hauteur_min INTEGER,
    hauteur_max INTEGER,
    protection BOOLEAN DEFAULT FALSE,
    photochromic BOOLEAN DEFAULT FALSE,
    tags TEXT,
    image_gravure TEXT
)
```
**Fonction** : Table finale pour l'API avec données enrichies

**Création des index** :
```sql
CREATE INDEX idx_enhanced_fournisseur ON enhanced (fournisseur)
CREATE INDEX idx_enhanced_materiaux ON enhanced (materiaux)
CREATE INDEX idx_verres_nom ON verres (nom)
CREATE INDEX idx_verres_fournisseur ON verres (fournisseur)
CREATE INDEX idx_verres_materiaux ON verres (materiaux)
```
**Fonction** : Optimisation des performances de recherche

#### **B. Requêtes d'Extraction et Sélection**

**Fichier** : `src/data/processing/cleaner.py`

**Extraction depuis staging** :
```sql
SELECT
    id, source_url, nom_verre, gravure_nasale,
    indice, materiaux, fournisseur
FROM staging
ORDER BY id
```
**Fonction** : Chargement des données brutes pour nettoyage

**Extraction depuis enhanced** :
```sql
SELECT
    id, nom_verre, materiaux, indice, fournisseur,
    gravure_nasale, source_url, created_at
FROM enhanced
ORDER BY id
```
**Fonction** : Chargement des données nettoyées pour enrichissement

**Fichier** : `src/data/export/csv_export.py`

**Statistiques de staging** :
```sql
SELECT COUNT(*) FROM staging
SELECT COUNT(DISTINCT fournisseur) FROM staging
SELECT fournisseur, COUNT(*) as nb_verres
FROM staging
GROUP BY fournisseur
ORDER BY nb_verres DESC
```
**Fonction** : Analyse et statistiques des données brutes

**Fichier** : `src/data/export/quick_export.py`

**Export complet staging** :
```sql
SELECT * FROM staging ORDER BY id
```
**Fonction** : Export rapide de toutes les données brutes

**Fichier** : `src/data/processing/enricher.py`

**Chargement enhanced pour enrichissement** :
```sql
SELECT * FROM enhanced ORDER BY id
```
**Fonction** : Chargement des données pour traitement enrichissement

#### **C. Requêtes d'Insertion et Mise à Jour**

**Fichier** : `src/data/processing/cleaner.py`

**Insertion dans enhanced** :
```sql
INSERT INTO enhanced (
    nom_verre, materiaux, indice, fournisseur,
    gravure_nasale, source_url
) VALUES (:nom_verre, :materiaux, :indice, :fournisseur,
          :gravure_nasale, :source_url)
```
**Fonction** : Insertion des données nettoyées

**Insertion dans verres** :
```sql
INSERT INTO verres (
    nom, materiau, indice, fournisseur, gravure
) VALUES (:nom, :materiau, :indice, :fournisseur, :gravure)
```
**Fonction** : Insertion des données finales pour l'API

**Insertion depuis CSV** :
```sql
INSERT INTO staging (
    source_url, nom_verre, gravure_nasale,
    indice, materiaux, fournisseur
) VALUES (:source_url, :nom_verre, :gravure_nasale,
          :indice, :materiaux, :fournisseur)
```
**Fonction** : Import de données depuis fichiers CSV

#### **D. Requêtes de Gestion des Références**

**Fichier** : `src/data/processing/cleaner.py`

**Extraction des fournisseurs** :
```sql
SELECT id FROM fournisseurs
```
**Fonction** : Récupération des IDs de référence fournisseurs

**Extraction des matériaux** :
```sql
SELECT id FROM materiaux
```
**Fonction** : Récupération des IDs de référence matériaux

**Insertion fournisseur** :
```sql
INSERT INTO fournisseurs (nom) VALUES (:nom)
```
**Fonction** : Création de nouveaux fournisseurs

**Insertion matériau** :
```sql
INSERT INTO materiaux (nom) VALUES (:nom)
```
**Fonction** : Création de nouveaux matériaux

#### **E. Requêtes de Correction et Maintenance**

**Fichier** : `src/data/processing/fix_enhanced_table.py`

**Vérification des valeurs problématiques** :
```sql
SELECT hauteur_max, hauteur_min, fournisseur_id, materiau_id
FROM enhanced
WHERE hauteur_max = 35 OR hauteur_min = 14
OR fournisseur_id IS NULL OR materiau_id IS NULL
```
**Fonction** : Identification des données à corriger

**Correction des hauteurs par défaut** :
```sql
UPDATE enhanced SET hauteur_max = NULL WHERE hauteur_max = 35
UPDATE enhanced SET hauteur_min = NULL WHERE hauteur_min = 14
```
**Fonction** : Suppression des valeurs par défaut incorrectes

**Liaison des fournisseurs** :
```sql
UPDATE e
SET e.fournisseur_id = f.id
FROM enhanced e
INNER JOIN fournisseurs f ON e.fournisseur = f.nom
WHERE e.fournisseur_id IS NULL
```
**Fonction** : Association automatique des fournisseurs

**Liaison des matériaux** :
```sql
UPDATE e
SET e.materiau_id = m.id
FROM enhanced e
INNER JOIN materiaux m ON e.materiaux = m.nom
WHERE e.materiau_id IS NULL
```
**Fonction** : Association automatique des matériaux

**Statistiques de correction** :
```sql
SELECT COUNT(*) as count,
    SUM(CASE WHEN hauteur_max = 35 THEN 1 ELSE 0 END) as default_hauteur_max,
    SUM(CASE WHEN hauteur_min = 14 THEN 1 ELSE 0 END) as default_hauteur_min,
    SUM(CASE WHEN fournisseur_id IS NULL THEN 1 ELSE 0 END) as null_fournisseur,
    SUM(CASE WHEN materiau_id IS NULL THEN 1 ELSE 0 END) as null_materiau
FROM enhanced
```
**Fonction** : Analyse des résultats de correction

#### **F. Requêtes d'Authentification et Sécurité**

**Fichier** : `src/api_ia/app/security.py`

**Authentification utilisateur** :
```sql
SELECT id, username, hashed_password FROM users WHERE username = :username
```
**Fonction** : Vérification des identifiants de connexion

**Récupération utilisateur** :
```sql
SELECT id, username, email FROM users WHERE username = :username
```
**Fonction** : Obtention des informations utilisateur

#### **G. Requêtes de l'API et Recherche**

**Fichier** : `src/api_ia/app/database.py`

**Récupération de tous les verres** :
```sql
SELECT * FROM verres
```
**Fonction** : Liste complète des verres pour l'API

**Détails d'un verre** :
```sql
SELECT * FROM verres WHERE id = :verre_id
```
**Fonction** : Informations détaillées d'un verre spécifique

**Détails d'un verre staging** :
```sql
SELECT * FROM verres_staging WHERE id = :verre_id
```
**Fonction** : Informations d'un verre dans la table staging

**Suppression d'utilisateur** :
```sql
DELETE FROM users WHERE username = :username
```
**Fonction** : Suppression d'un compte utilisateur

#### **H. Requêtes de Comptage et Validation**

**Fichier** : `src/data/processing/cleaner.py`

**Comptage des verres** :
```sql
SELECT COUNT(*) FROM verres
```
**Fonction** : Validation du nombre d'enregistrements

**Fichier** : `scripts/run_spiders.py`

**Comptage staging** :
```sql
SELECT COUNT(*) FROM staging
```
**Fonction** : Validation des données extraites par scraping

#### **I. Requêtes de Suppression et Nettoyage**

**Fichier** : `src/database/reset_database.py`

**Suppression des tables** :
```sql
DROP TABLE IF EXISTS verres CASCADE
DROP TABLE IF EXISTS enhanced CASCADE
DROP TABLE IF EXISTS staging CASCADE
```
**Fonction** : Réinitialisation complète de la base de données

**Fichier** : `src/data/processing/enricher.py`

**Vidage de la table verres** :
```sql
DELETE FROM verres
```
**Fonction** : Nettoyage avant nouvelle insertion

**Fichier** : `src/data/processing/cleaner.py`

**Suppression de la table enhanced** :
```sql
DROP TABLE IF EXISTS enhanced
```
**Fonction** : Recréation de la table enhanced

---

## 3. Traitement et Nettoyage des Données

### 3.1 Pipeline ETL Automatisé

Le système implémente un pipeline ETL (Extract, Transform, Load) complet :

**Extract (Extraction)** :
- **Web scraping** : Spiders Scrapy pour sites web
- **Fichiers** : Import automatique CSV et images
- **Base de données** : Requêtes SQL optimisées pour extraction depuis tables sources

**Transform (Transformation)** :
- **Nettoyage** : Suppression espaces, normalisation formats
- **Enrichissement** : Ajout tags, détection propriétés
- **Validation** : Contrôle qualité des données
- **Agrégation** : Consolidation de sources multiples
- **Homogénéisation** : Standardisation des formats

**Load (Chargement)** :
- **Staging** : Données brutes extraites
- **Enhanced** : Données nettoyées et enrichies
- **Production** : Données finales pour l'API

### 3.2 Règles d'Agrégation et d'Homogénéisation des Données

**Fichier principal** : `src/data/processing/cleaner.py`

Le projet implémente un système complet de règles d'agrégation et d'homogénéisation pour préparer le stockage du jeu de données final :

#### **A. Règles de Suppression des Entrées Corrompues**

**1. Suppression des Lignes avec Valeurs Manquantes Essentielles**
```python
# Suppression des lignes sans nom_verre, materiaux ou fournisseur
df = df.dropna(subset=["nom_verre", "materiaux", "fournisseur"])
```
**Fonction** : Élimine les enregistrements incomplets qui ne peuvent pas être traités

**2. Suppression des Doublons**
```python
# Suppression des enregistrements dupliqués
df = df.drop_duplicates()
```
**Fonction** : Élimine les données redondantes issues de sources multiples

**3. Validation des Indices de Réfraction**
```python
# Correction des valeurs hors plage (1.0 à 2.0)
invalid_before = len(df[df["indice"] < 1.0]) + len(df[df["indice"] > 2.0])
df.loc[df["indice"] < 1.0, "indice"] = 1.5
df.loc[df["indice"] > 2.0, "indice"] = 1.5
```
**Fonction** : Corrige les valeurs d'indice physiquement impossibles

**4. Suppression des Valeurs Par Défaut Incorrectes**
```sql
-- Suppression des hauteurs par défaut incorrectes
UPDATE enhanced SET hauteur_max = NULL WHERE hauteur_max = 35
UPDATE enhanced SET hauteur_min = NULL WHERE hauteur_min = 14
```
**Fichier** : `src/data/processing/fix_enhanced_table.py`
**Fonction** : Élimine les valeurs par défaut qui masquent des données réelles

#### **B. Règles d'Homogénéisation des Formats**

**1. Normalisation des Chaînes de Caractères**
```python
# Nettoyage des colonnes string
string_columns = ["nom_verre", "materiaux", "fournisseur", "gravure_nasale"]
for col in string_columns:
    df[col] = df[col].astype(str).str.strip()
    df[col] = df[col].str.replace(r"\s+", " ", regex=True)
```
**Fonction** : Supprime les espaces multiples et normalise les espaces

**2. Standardisation des Indices de Réfraction**
```python
# Conversion des virgules en points décimaux
df["indice"] = df["indice"].astype(str).str.replace(",", ".")

# Extraction des valeurs numériques
df["indice"] = df["indice"].str.extract(r"(\d+[.,]?\d*)").iloc[:, 0]

# Gestion des valeurs manquantes
df["indice"] = df["indice"].fillna("1.5")

# Conversion en float et arrondi
df["indice"] = pd.to_numeric(df["indice"], errors="coerce").fillna(1.5)
df["indice"] = df["indice"].round(2)
```
**Fonction** : Standardise le format des indices (virgules → points, arrondi à 2 décimales)

**3. Nettoyage des Noms de Verres**
```python
def clean_nom(self, nom: str) -> str:
    # Enlever les hauteurs
    nom = re.sub(r"\d+\s*[-/]\s*\d+\s*mm", "", nom)
    nom = re.sub(r"\d+\s*mm", "", nom)
    # Enlever les espaces multiples
    nom = " ".join(nom.split())
    return nom.strip()
```
**Fichier** : `src/data/processing/enricher.py`
**Fonction** : Supprime les informations de hauteur et normalise les espaces

#### **C. Règles d'Agrégation Multi-Sources**

**1. Consolidation des Fournisseurs**
```python
# Gestion des références fournisseurs
for fournisseur in df["fournisseur"].unique():
    if pd.isna(fournisseur):
        continue
    
    # Vérifier si le fournisseur existe
    cursor.execute("SELECT id FROM fournisseurs WHERE nom = ?", (fournisseur,))
    result = cursor.fetchone()
    
    if not result:
        # Créer le fournisseur
        cursor.execute("INSERT INTO fournisseurs (nom) VALUES (?)", (fournisseur,))
```
**Fonction** : Unifie les références fournisseurs depuis différentes sources

**2. Consolidation des Matériaux**
```python
# Gestion des références matériaux
for materiau in df["materiaux"].unique():
    if pd.isna(materiau):
        continue
    
    # Vérifier si le matériau existe
    cursor.execute("SELECT id FROM materiaux WHERE nom = ?", (materiau,))
    result = cursor.fetchone()
    
    if not result:
        # Créer le matériau
        cursor.execute("INSERT INTO materiaux (nom) VALUES (?)", (materiau,))
```
**Fonction** : Unifie les références matériaux depuis différentes sources

**3. Liaison Automatique des Références**
```sql
-- Liaison automatique des fournisseurs
UPDATE e
SET e.fournisseur_id = f.id
FROM enhanced e
INNER JOIN fournisseurs f ON e.fournisseur = f.nom
WHERE e.fournisseur_id IS NULL

-- Liaison automatique des matériaux
UPDATE e
SET e.materiau_id = m.id
FROM enhanced e
INNER JOIN materiaux m ON e.materiaux = m.nom
WHERE e.materiau_id IS NULL
```
**Fichier** : `src/data/processing/fix_enhanced_table.py`
**Fonction** : Associe automatiquement les références manquantes

#### **D. Règles d'Enrichissement Automatique**

**1. Extraction de Variantes**
```python
def extract_variante(self, nom_complet: str, nom_base: str) -> str:
    if not nom_base or not nom_complet:
        return ""
    variante = nom_complet.replace(nom_base, "").strip()
    return variante if variante else ""
```
**Fonction** : Identifie automatiquement les variantes de verres

**2. Détection de Propriétés**
```python
def detect_protection(self, nom: str) -> bool:
    nom_lower = nom.lower()
    return any(keyword in nom_lower for keyword in self.PROTECTION_KEYWORDS)

def detect_photochromic(self, nom: str) -> bool:
    nom_lower = nom.lower()
    return any(keyword in nom_lower for keyword in self.PHOTOCHROMIC_KEYWORDS)
```
**Fonction** : Détecte automatiquement les propriétés de protection et photochromie

**3. Extraction de Tags**
```python
def extract_tags(self, nom: str) -> List[str]:
    tags = []
    nom_lower = nom.lower()
    
    # Détection du type de verre
    if any(x in nom_lower for x in ["progress", "varilux"]):
        tags.append("progressif")
    elif "unifocal" in nom_lower:
        tags.append("unifocal")
    
    # Détection des traitements
    if self.detect_protection(nom):
        tags.append("protection")
    if self.detect_photochromic(nom):
        tags.append("photochromique")
    
    return list(set(tags))  # Enlever les doublons
```
**Fonction** : Génère automatiquement des tags de classification

**4. Extraction de Hauteurs**
```python
def extract_hauteurs(self, nom: str) -> tuple:
    hauteur_pattern = r"(\d+)(?:\s*[-/]\s*(\d+))?\s*mm"
    match = re.search(hauteur_pattern, nom)
    
    if match:
        min_h = int(match.group(1))
        max_h = int(match.group(2)) if match.group(2) else min_h
        return min_h, max_h
    return None, None
```
**Fonction** : Extrait automatiquement les hauteurs depuis les noms de verres

#### **E. Scripts d'Automatisation du Nettoyage**

**1. Script de Nettoyage Principal**
```python
def process_and_export(self, create_enhanced_table=True):
    # 1. Chargement des données
    df_raw = self.load_data_from_staging()
    
    # 2. Nettoyage des données
    df_clean = self.clean_dataframe(df_raw)
    
    # 3. Export CSV
    csv_path = self.export_enhanced_to_csv(df_clean)
    
    # 4. Création et insertion dans la table enhanced
    if create_enhanced_table:
        self.create_enhanced_table()
        self.insert_to_enhanced(df_clean)
```
**Fonction** : Pipeline complet de nettoyage et export

**2. Script de Correction Post-Nettoyage**
```python
def fix_enhanced_table():
    # 1. Vérifier les valeurs problématiques
    # 2. Mettre à jour les hauteurs par défaut
    # 3. Lier les IDs manquants
    # 4. Vérifier les résultats
```
**Fichier** : `src/data/processing/fix_enhanced_table.py`
**Fonction** : Correction automatique des données après nettoyage

**3. Script d'Enrichissement**
```python
def process_enhanced_to_verres(self):
    # 1. Charger les données enhanced
    # 2. Enrichir les données
    # 3. Insérer dans la table verres
```
**Fichier** : `src/data/processing/enricher.py`
**Fonction** : Enrichissement automatique des données nettoyées

### 3.3 Nettoyage Automatique

**Fichier** : `src/data/processing/cleaner.py`

La classe `OpticalDataCleaner` effectue :

```python
class OpticalDataCleaner:
    def clean_data(self):
        # Chargement depuis la table staging
        # Nettoyage des données
        # Création de la table enhanced
        # Export CSV
        # Statistiques de nettoyage
```

**Actions automatisées** :
- Chargement des données depuis la table `staging`
- Nettoyage et normalisation des formats (suppression espaces, conversion indice)
- Suppression des lignes avec valeurs manquantes essentielles
- Création de la table `enhanced`
- Export des données nettoyées en CSV
- Statistiques de nettoyage

### 3.4 Enrichissement des Données

**Fichier** : `src/data/processing/enricher.py`

La classe `DataEnricher` enrichit automatiquement les données :

- Extraction de variantes depuis les noms de verres
- Détection automatique de propriétés (protection UV, photochromique)
- Extraction de tags pertinents (progressif, unifocal, transitions, polarisant)
- Extraction de hauteurs min/max depuis les noms
- Nettoyage et normalisation des noms de verres
- Passage de `enhanced` vers `verres`

### 3.5 Automatisation Multi-Sources

**Intégration de données hétérogènes** :
- **Web scraping** : Données structurées depuis sites web
- **Fichiers images** : Métadonnées et traitement automatique
- **CSV externes** : Import de données complémentaires
- **Base de données** : Synchronisation et consolidation

---

## 4. Orchestration Automatisée

### 4.1 Gestionnaire de Pipeline Multi-Sources

Le `PipelineManager` orchestre l'extraction depuis toutes les sources :

**Sources Web** :
- Exécution automatique des spiders Scrapy
- Gestion des délais et respect des robots.txt
- Rotation des User-Agents

**Fichiers de Données** :
- Surveillance automatique des nouveaux fichiers
- Traitement par lots des images
- Import automatique des CSV

**Base de Données** :
- Synchronisation automatique entre tables
- Mise à jour incrémentale des données
- Gestion des conflits et doublons

### 4.2 Gestionnaire de Pipeline

**Fichier** : `src/orchestrator/pipeline_manager.py`

Le `PipelineManager` orchestre l'ensemble du flux :

```python
class PipelineManager:
    def run_full_pipeline(self) -> Dict[str, bool]:
        """
        Exécute le pipeline complet :
        1. Scraping des données
        2. Nettoyage
        3. Enrichissement
        4. Import final
        """
```

**Fonctionnalités** :
- Chargement dynamique des spiders Scrapy
- Exécution séquentielle des étapes (spiders puis nettoyage)
- Monitoring et logging unifié
- Gestion des erreurs par étape
- Résultats détaillés par composant

### 4.3 Scripts d'Automatisation Multi-Sources

**Scripts disponibles** :
- `src/scripts/extract_tags.py` : Extraction automatique des tags depuis base de données
- `src/scripts/insert_tags.py` : Insertion des tags en base de données
- `src/datasets/split_dataset.py` : Division automatique des datasets d'images
- `src/datasets/triplet_dataset.py` : Création de triplets pour l'entraînement
- `src/data/processing/cleaner.py` : Nettoyage automatique depuis fichiers et base
- `src/data/processing/enricher.py` : Enrichissement automatique multi-sources
- `src/data/export/csv_export.py` : Export SQL vers CSV avec requêtes optimisées
- `src/api_ia/app/database.py` : Requêtes SQL pour l'API et recherche intelligente

---

## 5. Gestion des Images et Datasets

### 5.1 Structure des Données

Le projet utilise une structure organisée pour les images :

```
data/
├── raw_gravures/          # Images brutes extraites
├── augmented_gravures/     # Images augmentées
├── oversampled_gravures/   # Images rééquilibrées
├── split/                 # Datasets divisés (train/val/test)
└── media/gravures/        # Images pour l'API
```

### 5.2 Automatisation du Split Dataset

**Fichier** : `src/datasets/split_dataset.py`

```python
def split_dataset(source_dir: str, target_dir: str, split_ratios: Tuple[float, float, float]):
    """
    Divise automatiquement le dataset en :
    - 70% train
    - 15% validation  
    - 15% test
    """
```

**Fonctionnalités** :
- Division automatique par classe
- Respect des ratios configurés
- Préservation de la structure
- Reproducibilité avec seed

---

## 6. Conception de la Base de Données en Respect du RGPD

### 6.1 Modèle Conceptuel de Données (MCD)

Le projet EngraveDetect utilise une approche **Merise** pour la modélisation conceptuelle des données, respectant les principes du RGPD :

#### **A. Entités Principales**

**1. Verre (Entité Centrale)**
- **Attributs** : id, nom, materiaux, indice, fournisseur, gravure, url_source
- **Attributs enrichis** : variante, hauteur_min, hauteur_max, protection, photochromic, tags, image_gravure
- **Contrainte RGPD** : Aucune donnée personnelle, uniquement des données techniques

**2. Fournisseur (Entité de Référence)**
- **Attributs** : id, nom
- **Contrainte RGPD** : Données publiques des fabricants, pas de données personnelles

**3. Matériau (Entité de Référence)**
- **Attributs** : id, nom
- **Contrainte RGPD** : Données techniques publiques

**4. Utilisateur (Entité RGPD)**
- **Attributs** : id, username, email, hashed_password
- **Contrainte RGPD** : Données minimales, chiffrement des mots de passe

#### **B. Relations Conceptuelles**

```
Verre (1) -----> (1) Fournisseur
Verre (1) -----> (1) Matériau
Utilisateur (1) -----> (0,N) Session_Auth
```

#### **C. Principes RGPD Appliqués**

**1. Minimisation des Données**
- Collecte uniquement des données techniques nécessaires
- Pas de collecte de données personnelles superflues
- Anonymisation des données de recherche

**2. Finalité Limitée**
- Données utilisées uniquement pour la classification de gravures
- Pas de réutilisation à des fins commerciales
- Traçabilité des usages

**3. Conservation Limitée**
- Données techniques conservées selon les besoins métier
- Données utilisateur supprimables à la demande
- Politique de rétention documentée

### 6.2 Modèle Physique de Données (MPD)

**Fichier principal** : `src/database/reset_database.py`

#### **A. Tables de Données Techniques**

**1. Table `staging` (Zone de Transit)**
```sql
CREATE TABLE staging (
    id SERIAL PRIMARY KEY,
    source_url TEXT,
    nom_verre TEXT,
    gravure_nasale TEXT,
    indice DOUBLE PRECISION,
    materiaux VARCHAR(100),
    fournisseur VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
**Fonction** : Stockage temporaire des données brutes extraites
**RGPD** : Données techniques uniquement, pas de données personnelles

**2. Table `enhanced` (Zone de Traitement)**
```sql
CREATE TABLE enhanced (
    id SERIAL PRIMARY KEY,
    nom_du_verre TEXT,
    materiaux VARCHAR(100),
    indice DOUBLE PRECISION,
    fournisseur VARCHAR(100),
    gravure_nasale TEXT,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
**Fonction** : Données nettoyées et préparées
**RGPD** : Traitement automatisé sans intervention humaine

**3. Table `verres` (Zone de Production)**
```sql
CREATE TABLE verres (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    materiaux VARCHAR(100),
    indice DOUBLE PRECISION,
    fournisseur VARCHAR(100),
    gravure TEXT,
    url_source TEXT,
    variante VARCHAR(100),
    hauteur_min INTEGER,
    hauteur_max INTEGER,
    protection BOOLEAN DEFAULT FALSE,
    photochromic BOOLEAN DEFAULT FALSE,
    tags TEXT,
    image_gravure TEXT
)
```
**Fonction** : Données finales enrichies pour l'API
**RGPD** : Données techniques enrichies, pas de données personnelles

#### **B. Tables de Référence**

**1. Table `fournisseurs`**
```sql
CREATE TABLE fournisseurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) UNIQUE NOT NULL
)
```
**Fonction** : Normalisation des références fournisseurs
**RGPD** : Données publiques des fabricants

**2. Table `materiaux`**
```sql
CREATE TABLE materiaux (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) UNIQUE NOT NULL
)
```
**Fonction** : Normalisation des références matériaux
**RGPD** : Données techniques publiques

#### **C. Tables de Sécurité RGPD**

**1. Table `users` (Gestion des Utilisateurs)**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
**Fonction** : Authentification et gestion des comptes
**RGPD** : Données minimales, mots de passe chiffrés

**2. Table `security_events` (Audit RGPD)**
```sql
CREATE TABLE security_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) NOT NULL,
    message TEXT,
    username VARCHAR(100),
    ip_address VARCHAR(45)
)
```
**Fonction** : Traçabilité des accès et événements de sécurité
**RGPD** : Logs de sécurité pour audit et conformité

### 6.3 Modèles SQLAlchemy

**Fichier** : `src/api/models/verres.py`

```python
class Verre(Base):
    __tablename__ = "verres"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Données de base (reprises de enhanced)
    nom = Column(String(500), nullable=False)
    materiaux = Column(String(100))
    indice = Column(Float)
    fournisseur = Column(String(200))
    gravure = Column(String(1000), nullable=True)
    url_source = Column(String(500))
    
    # Données enrichies
    variante = Column(String(200))
    hauteur_min = Column(Integer)
    hauteur_max = Column(Integer)
    protection = Column(Boolean, default=False)
    photochromic = Column(Boolean, default=False)
    tags = Column(String(500))
    image_gravure = Column(String(500))
```

**Fonction** : Modèle ORM pour la table verres
**RGPD** : Validation des types et contraintes

### 6.4 Configuration de Sécurité

**Fichier** : `src/api/core/config.py`

```python
class Settings(BaseSettings):
    # Configuration base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Configuration sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS / Sécurité réseau
    allowed_hosts: str = os.getenv("ALLOWED_HOSTS")
    cors_origins: str = os.getenv("CORS_ORIGINS")
```

**Fonction** : Configuration sécurisée de la base de données
**RGPD** : Variables d'environnement pour la sécurité

### 6.5 Endpoints RGPD

**Fichier** : `src/api_ia/app/main.py`

#### **A. Droit d'Accès aux Données**
```python
@app.get("/me", response_model=UserResponse)
async def get_me(current_user: str = Depends(get_current_user)):
    """
    Endpoint RGPD pour obtenir les données personnelles de l'utilisateur authentifié.
    """
    user = get_user(current_user)
    # On ne retourne que les infos RGPD pertinentes
    return UserResponse(username=user["username"], email=user["email"])
```

#### **B. Droit à l'Oubli**
```python
@app.delete("/me", response_model=DeleteResponse)
async def delete_me(current_user: str = Depends(get_current_user)):
    """
    Endpoint RGPD pour supprimer le compte de l'utilisateur authentifié (droit à l'oubli).
    """
    success = delete_user_by_username(current_user)
    log_security_event("USER_DELETED", f"Suppression du compte pour {current_user}")
    return DeleteResponse(message="Compte supprimé avec succès")
```

### 6.6 Pipeline de Données Multi-Sources

Le flux de données traverse plusieurs tables avec intégration de sources variées :

1. **staging** : Données brutes extraites (web scraping + fichiers)
2. **enhanced** : Données nettoyées et enrichies (multi-sources)
3. **verres** : Données finales consolidées pour l'API

**Sources intégrées** :
- **Web scraping** : Données structurées depuis sites web
- **Fichiers images** : Métadonnées et chemins de fichiers
- **CSV externes** : Données complémentaires importées
- **Base de données** : Données existantes synchronisées

### 6.7 Programmation de l'Import des Données

**Fichier principal** : `src/data/processing/cleaner.py`

#### **A. Script d'Import Automatisé**

```python
def process_and_export(self, create_enhanced_table=True):
    """
    Pipeline complet d'import et de traitement des données :
    1. Chargement depuis staging
    2. Nettoyage et homogénéisation
    3. Export CSV
    4. Import dans enhanced
    """
    # 1. Chargement des données
    df_raw = self.load_data_from_staging()
    
    # 2. Nettoyage des données
    df_clean = self.clean_dataframe(df_raw)
    
    # 3. Export CSV
    csv_path = self.export_enhanced_to_csv(df_clean)
    
    # 4. Création et insertion dans la table enhanced
    if create_enhanced_table:
        self.create_enhanced_table()
        self.insert_to_enhanced(df_clean)
```

#### **B. Import depuis CSV**

```python
def insert_from_enhanced_csv(self, csv_path: str) -> bool:
    """
    Import automatique depuis un fichier CSV vers la table staging.
    """
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        with self.get_connection() as conn:
            for row in reader:
                conn.execute(
                    text("""
                        INSERT INTO staging (
                            source_url, nom_verre, gravure_nasale,
                            indice, materiaux, fournisseur
                        ) VALUES (:source_url, :nom_verre, :gravure_nasale, 
                                :indice, :materiaux, :fournisseur)
                    """),
                    {
                        "source_url": row["source_url"],
                        "nom_verre": row["nom_verre"],
                        "gravure_nasale": row["gravure_nasale"],
                        "indice": row["indice"],
                        "materiaux": row["materiaux"],
                        "fournisseur": row["fournisseur"],
                    },
                )
            conn.commit()
```

#### **C. Import vers Table Finale**

```python
def insert_to_verres(self, df: pd.DataFrame) -> bool:
    """
    Import des données enrichies vers la table verres (production).
    """
    # Préparer les données pour la table verres
    df_verres = self._prepare_data_for_verres(df)
    
    # Vérifier que la table est vide
    with self.get_connection() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM verres"))
        count = result.fetchone()[0]
        if count > 0:
            conn.execute(text("TRUNCATE TABLE verres"))
    
    # Insertion des données
    for index, row in df_verres.iterrows():
        conn.execute(
            text("""
                INSERT INTO verres (
                    nom, materiau, indice, fournisseur, gravure
                ) VALUES (:nom, :materiau, :indice, :fournisseur, :gravure)
            """),
            {
                "nom": row["nom"],
                "materiau": row["materiau"],
                "indice": row["indice"],
                "fournisseur": row["fournisseur"],
                "gravure": row["gravure"],
            },
        )
```

#### **D. Gestion des Références**

```python
def _handle_references(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Gestion automatique des références fournisseurs et matériaux.
    """
    # Créer d'abord les tables de référence
    self.create_reference_tables()
    
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        # Gestion des fournisseurs
        for fournisseur in df["fournisseur"].unique():
            if pd.isna(fournisseur):
                continue
            
            # Vérifier si le fournisseur existe
            cursor.execute("SELECT id FROM fournisseurs WHERE nom = ?", (fournisseur,))
            result = cursor.fetchone()
            
            if not result:
                # Créer le fournisseur
                cursor.execute("INSERT INTO fournisseurs (nom) VALUES (?)", (fournisseur,))
```

#### **E. Validation et Contrôle Qualité**

```python
def get_data_statistics(self, df: pd.DataFrame):
    """
    Validation et statistiques des données importées.
    """
    # Statistiques de base
    self.logger.info(f"Nombre total de lignes : {len(df)}")
    self.logger.info(f"Nombre de colonnes : {len(df.columns)}")
    
    # Statistiques par fournisseur
    fournisseur_stats = df["fournisseur"].value_counts()
    self.logger.info("\nRépartition par fournisseur :")
    for fournisseur, count in fournisseur_stats.items():
        self.logger.info(f"   • {fournisseur}: {count} verres")
    
    # Statistiques par indice
    indice_stats = df["indice"].value_counts()
    self.logger.info("\nRépartition par indice :")
    for indice, count in indice_stats.items():
        self.logger.info(f"   • {indice}: {count} verres")
```

#### **F. Commandes d'Import**

```bash
# Import complet des données
python -m src.data.processing.cleaner

# Import depuis CSV spécifique
python -m src.data.processing.import_enhanced

# Réinitialisation complète de la base
python -m src.database.reset_database

# Import avec validation
python -c "from src.data.processing.cleaner import OpticalDataCleaner; cleaner = OpticalDataCleaner(); cleaner.process_and_export()"
```

#### **G. Sécurité RGPD lors de l'Import**

**1. Validation des Données**
- Vérification de l'absence de données personnelles
- Contrôle des types de données
- Validation des contraintes métier

**2. Traçabilité**
- Logs de tous les imports
- Horodatage des opérations
- Traçabilité des sources

**3. Gestion des Erreurs**
- Rollback en cas d'erreur
- Logs d'erreurs détaillés
- Notification des problèmes

**4. Contrôle d'Accès**
- Authentification requise pour les imports
- Autorisations granulaires
- Audit des opérations

### 6.8 Automatisation des Corrections

**Fichier** : `src/data/processing/fix_enhanced_table.py`

Corrections automatiques post-nettoyage :
- Correction des valeurs par défaut
- Liaison des IDs manquants
- Validation des contraintes

---

## 7. Partage du Jeu de Données via Interfaces Logicielles

### 7.1 Architecture des Interfaces de Partage

Le projet EngraveDetect met en place un système complet d'interfaces logicielles pour partager le jeu de données et le rendre accessible pour le développement du projet :

#### **A. Interfaces API REST**

**Fichier principal** : `src/api/main.py`

**Configuration FastAPI** :
```python
app = FastAPI(
    title="API Verres Optiques",
    version=settings.APP_VERSION,
    description=settings.API_DESCRIPTION,
)

# Configuration CORS pour l'accès multi-origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Fonction** : Interface principale pour l'accès aux données
**RGPD** : Authentification et autorisation requises

#### **B. Interfaces Programmables**

**1. API REST pour Verres**
**Fichier** : `src/api/routes/v1/verres.py`

```python
@router.get("/", response_model=VerreList)
async def read_verres(
    skip: int = 0,
    limit: int = 100,
    fournisseur: Optional[str] = None,
    materiaux: Optional[str] = None,
    indice_min: Optional[float] = None,
    indice_max: Optional[float] = None,
    protection: Optional[bool] = None,
    photochromic: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Liste des verres avec filtres optionnels."""
```

**Endpoints disponibles** :
- `GET /api/v1/verres/` : Liste paginée avec filtres
- `GET /api/v1/verres/{id}` : Détails d'un verre
- `GET /api/v1/verres/fournisseurs/list` : Liste des fournisseurs
- `GET /api/v1/verres/materiaux/list` : Liste des matériaux
- `GET /api/v1/verres/stats/general` : Statistiques générales
- `POST /api/v1/verres/` : Création d'un verre
- `PUT /api/v1/verres/{id}` : Mise à jour d'un verre
- `DELETE /api/v1/verres/{id}` : Suppression d'un verre

**2. API IA pour Classification**
**Fichier** : `src/api_ia/app/main.py`

```python
@app.post("/match", response_model=MatchResponse)
@limiter.limit("5/minute")
async def get_best_match(request: Request, file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    """Endpoint pour obtenir les meilleures correspondances de classes pour une image."""
```

**Endpoints IA disponibles** :
- `POST /embedding` : Génération d'embeddings d'images
- `POST /match` : Classification d'images de gravures
- `POST /search_tags` : Recherche par tags
- `GET /verre/{id}` : Détails d'un verre par ID
- `GET /health` : Vérification de santé
- `GET /model/health` : Santé du modèle d'IA

### 7.2 Schémas de Données et Validation

**Fichier** : `src/api/schemas/verres.py`

#### **A. Schémas Pydantic**

```python
class VerreBase(BaseModel):
    """Schéma de base pour les verres."""
    nom: str = Field(..., description="Nom du verre")
    fournisseur: str = Field(..., description="Fournisseur du verre")
    materiaux: str = Field(..., description="Matériau du verre")
    indice: float = Field(..., description="Indice de réfraction")
    protection: bool = Field(False, description="Présence de protection")
    photochromic: bool = Field(False, description="Verre photochromique")
    hauteur_min: Optional[float] = Field(None, description="Hauteur minimale en mm")
    hauteur_max: Optional[float] = Field(None, description="Hauteur maximale en mm")
    gravure: Optional[str] = Field(None, description="Code de gravure nasale")

class VerreResponse(VerreBase):
    """Schéma de réponse pour un verre."""
    id: int = Field(..., description="Identifiant unique du verre")
    model_config = {"from_attributes": True}

class VerreList(BaseModel):
    """Schéma de réponse pour la liste des verres."""
    total: int = Field(..., description="Nombre total de verres")
    items: List[VerreResponse] = Field(..., description="Liste des verres")

class VerreFilters(BaseModel):
    """Schéma pour les filtres de recherche."""
    fournisseur: Optional[str] = None
    materiaux: Optional[str] = None
    indice_min: Optional[float] = None
    indice_max: Optional[float] = None
    protection: Optional[bool] = None
    photochromic: Optional[bool] = None
```

**Fonction** : Validation automatique des données entrantes et sortantes
**RGPD** : Contrôle des types et formats de données

### 7.3 Services de Données

**Fichier** : `src/api/services/verres.py`

#### **A. Services de Récupération**

```python
def get_verres(db: Session, filters: Optional[VerreFilters] = None, skip: int = 0, limit: int = 100) -> VerreList:
    """Récupère la liste des verres avec filtres optionnels."""
    query = db.query(Verre)

    if filters:
        # Application des filtres
        if filters.fournisseur:
            query = query.filter(Verre.fournisseur == filters.fournisseur)
        if filters.materiaux:
            query = query.filter(Verre.materiaux == filters.materiaux)
        if filters.indice_min is not None:
            query = query.filter(Verre.indice >= filters.indice_min)
        if filters.indice_max is not None:
            query = query.filter(Verre.indice <= filters.indice_max)
        if filters.protection is not None:
            query = query.filter(Verre.protection == filters.protection)
        if filters.photochromic is not None:
            query = query.filter(Verre.photochromic == filters.photochromic)

    total = query.count()
    items = query.order_by(Verre.id).offset(skip).limit(limit).all()
    verre_responses = [VerreResponse.model_validate(verre) for verre in items]
    return VerreList(total=total, items=verre_responses)
```

#### **B. Services de Statistiques**

```python
def get_stats(db: Session) -> dict:
    """Récupère les statistiques générales."""
    return {
        "total_verres": db.query(Verre).count(),
        "total_fournisseurs": db.query(Verre.fournisseur).distinct().count(),
        "total_materiaux": db.query(Verre.materiaux).distinct().count(),
    }
```

### 7.4 Interface Frontend

**Fichier** : `src/front/api.js`

#### **A. Client API JavaScript**

```javascript
// Configuration des URLs d'API
const API_URL = 'http://localhost:8000/api/v1';
const API_IA_URL = 'http://localhost:8001';

// Fonction pour obtenir le token d'authentification
function getToken() {
    return localStorage.getItem('token');
}

// Fonction de connexion
export async function login(email, password) {
    try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            body: formData
        });

        const data = await response.json();
        setToken(data.access_token);
        return data;
    } catch (error) {
        console.error('Erreur de connexion:', error);
        throw error;
    }
}
```

#### **B. Fonctions d'Accès aux Données**

```javascript
// Fonction pour obtenir des tags similaires
export async function getSimilarTags(imageData) {
    try {
        const token = getToken();
        if (!token) throw new Error('Non authentifié');

        const response = await fetch(`${API_IA_URL}/match`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        });

        return await response.json();
    } catch (error) {
        console.error('Erreur lors de la recherche de tags similaires:', error);
        throw error;
    }
}

// Fonction pour rechercher des verres par tags
export async function searchVerresByTags(tags) {
    try {
        const token = getToken();
        if (!token) throw new Error('Non authentifié');

        const response = await fetch(`${API_IA_URL}/search_tags`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tags)
        });

        return await response.json();
    } catch (error) {
        console.error('Erreur lors de la recherche de verres:', error);
        throw error;
    }
}
```

### 7.5 Interfaces de Développement

#### **A. Documentation OpenAPI/Swagger**

**Configuration** : `src/api/core/config.py`

```python
openapi_config = {
    "title": settings.APP_NAME,
    "version": settings.APP_VERSION,
    "description": settings.API_DESCRIPTION,
    "openapi_tags": [
        {"name": "verres", "description": "Opérations sur les verres optiques"},
        {"name": "auth", "description": "Authentification et gestion des tokens"},
    ],
    "docs_url": settings.DOCS_URL,
    "redoc_url": settings.REDOC_URL,
}
```

**Accès** :
- `/docs` : Documentation interactive Swagger
- `/redoc` : Documentation alternative ReDoc
- `/openapi.json` : Spécification OpenAPI

#### **B. Endpoints de Monitoring**

```python
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérifie que l'API est en fonctionnement."""
    return {"status": "healthy"}

@app.get("/model/health", response_model=ModelHealthResponse)
async def model_health_check():
    """Vérifie la santé du modèle d'IA."""
    try:
        model_status = model_monitor.get_model_health_status()
        return ModelHealthResponse(
            status="healthy", 
            model_metrics=model_status, 
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/metrics")
def metrics():
    """Endpoint Prometheus pour exporter les métriques de monitoring."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### 7.6 Sécurité et Contrôle d'Accès

#### **A. Authentification JWT**

```python
@app.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authentification et génération de token JWT."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user[0]:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    access_token = create_access_token({"sub": user[1]["username"]})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        version=settings.APP_VERSION
    )
```

#### **B. Rate Limiting**

```python
@app.post("/match", response_model=MatchResponse)
@limiter.limit("5/minute")  # Limite de 5 requêtes par minute
async def get_best_match(request: Request, file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    """Endpoint pour la classification d'images avec limitation de débit."""
```

#### **C. Validation des Fichiers**

```python
def validate_image_file(file_content: bytes, filename: Optional[str] = None) -> bool:
    """Valide qu'un fichier est bien une image."""
    try:
        # Vérification du type MIME
        mime_type = magic.from_buffer(file_content, mime=True)
        if not mime_type.startswith("image/"):
            return False

        # Vérification de l'extension
        if filename:
            allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
            file_extension = os.path.splitext(filename.lower())[1]
            if file_extension not in allowed_extensions:
                return False

        # Vérification de la taille (max 10MB)
        if len(file_content) > 10 * 1024 * 1024:
            return False

        return True
    except Exception as e:
        return False
```

### 7.7 Exemples d'Utilisation

#### **A. Requête cURL**

```bash
# Authentification
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password"

# Récupération des verres avec filtres
curl -X GET "http://localhost:8000/api/v1/verres/?fournisseur=Essilor&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Classification d'image
curl -X POST "http://localhost:8001/match" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@image.jpg"
```

#### **B. Client Python**

```python
import requests

# Configuration
API_URL = "http://localhost:8000/api/v1"
API_IA_URL = "http://localhost:8001"

# Authentification
auth_response = requests.post(f"{API_URL}/auth/token", data={
    "username": "user@example.com",
    "password": "password"
})
token = auth_response.json()["access_token"]

# Récupération des verres
headers = {"Authorization": f"Bearer {token}"}
verres_response = requests.get(f"{API_URL}/verres/", headers=headers)
verres = verres_response.json()

# Classification d'image
with open("image.jpg", "rb") as f:
    files = {"file": f}
    match_response = requests.post(f"{API_IA_URL}/match", headers=headers, files=files)
    matches = match_response.json()
```

#### **C. Client JavaScript**

```javascript
// Authentification
const loginResponse = await fetch(`${API_URL}/auth/token`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
        username: 'user@example.com',
        password: 'password'
    })
});
const { access_token } = await loginResponse.json();

// Récupération des verres
const verresResponse = await fetch(`${API_URL}/verres/?limit=10`, {
    headers: {
        'Authorization': `Bearer ${access_token}`
    }
});
const verres = await verresResponse.json();

// Classification d'image
const formData = new FormData();
formData.append('file', imageFile);
const matchResponse = await fetch(`${API_IA_URL}/match`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${access_token}`
    },
    body: formData
});
const matches = await matchResponse.json();
```

### 7.8 Configuration et Déploiement

#### **A. Variables d'Environnement**

```bash
# Configuration API
DATABASE_URL=postgresql://user:password@localhost/engravedetect
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration CORS
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Configuration serveur
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### **B. Commandes de Démarrage**

```bash
# Démarrage de l'API principale
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Démarrage de l'API IA
uvicorn src.api_ia.app.main:app --host 0.0.0.0 --port 8001 --reload

# Démarrage avec Docker
docker-compose up -d
```

---

## 7. Monitoring et Logging

### 7.1 Système de Logging

Tous les composants utilisent un système de logging unifié :

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

### 7.2 Monitoring des Performances

- Suivi des temps d'exécution
- Comptage des données traitées
- Détection des erreurs
- Statistiques de qualité

---

## 8. Exécution du Flux Automatisé

### 8.1 Commandes Principales

```bash
# Exécution du pipeline complet
python -m src.orchestrator.pipeline_manager

# Exécution d'un spider spécifique
scrapy crawl glass_spider

# Nettoyage des données
python -m src.data.processing.cleaner

# Enrichissement
python -m src.data.processing.enricher

# Division du dataset
python -m src.datasets.split_dataset

# Export SQL vers CSV
python -m src.data.export.csv_export

# Requêtes SQL personnalisées
python -c "from src.api_ia.app.database import execute_query; print(execute_query('SELECT COUNT(*) FROM verres'))"
```

### 8.2 Configuration

Le système utilise des variables d'environnement pour la configuration :
- `DATABASE_URL` : Connexion à la base de données
- `SCRAPING_DELAY` : Délai entre les requêtes
- `LOG_LEVEL` : Niveau de logging

---

## 9. Avantages du Flux Automatisé Multi-Sources

### 9.1 Efficacité
- Automatisation complète de l'extraction depuis france-optique.com
- Élimination des erreurs manuelles de saisie
- Traitement automatisé des données brutes vers données enrichies
- Intégration automatique de sources multiples (web, fichiers, base de données)
- Requêtes SQL optimisées pour l'extraction et l'analyse des données
- Règles d'agrégation et d'homogénéisation automatisées pour la qualité des données

### 9.2 Qualité
- Standardisation du nettoyage
- Validation automatique
- Traçabilité complète
- Requêtes SQL sécurisées avec paramètres
- Intégrité des données garantie par transactions
- Suppression automatique des entrées corrompues
- Homogénéisation des formats multi-sources
- Conformité RGPD intégrée dans la conception

### 9.3 Scalabilité
- Ajout facile de nouvelles sources (APIs, sites web, fichiers)
- Extension des traitements multi-formats
- Adaptation aux nouveaux formats de données
- Intégration de nouvelles bases de données

---

## 10. Maintenance et Évolution

### 10.1 Maintenance Préventive
- Monitoring régulier des performances multi-sources
- Mise à jour des spiders selon les changements de sites
- Optimisation des requêtes de base de données
- Surveillance des nouvelles sources de données
- Maintenance des connecteurs de fichiers et APIs

### 10.2 Évolutions Futures
- Intégration de nouvelles sources de données (APIs tierces, bases externes)
- Amélioration des algorithmes de nettoyage multi-formats
- Extension des fonctionnalités d'enrichissement
- Support de nouveaux formats de fichiers
- Intégration de services cloud pour le stockage
- Optimisation des requêtes SQL avec index avancés
- Développement de requêtes analytiques complexes

---

## Conclusion

Le flux automatisé de collecte des données d'EngraveDetect représente une solution complète et robuste pour l'extraction, le traitement et l'intégration des données de gravures optiques depuis **plusieurs sources** :

- **Services web et pages web** : Scraping automatisé de sites d'optique
- **Fichiers de données** : Traitement automatique d'images et CSV
- **Base de données** : Synchronisation et consolidation de données avec requêtes SQL optimisées

Cette automatisation multi-sources garantit la qualité, la cohérence et la disponibilité des données pour l'ensemble du système, tout en permettant une intégration flexible de nouvelles sources selon les besoins du projet.

Le développement de requêtes SQL spécifiques et optimisées assure une extraction efficace des données depuis PostgreSQL, avec des fonctionnalités avancées de recherche, d'analyse et de gestion des références.

**Les règles d'agrégation et d'homogénéisation** programment automatiquement la suppression des entrées corrompues et l'homogénéisation des formats des données, préparant ainsi un jeu de données final de haute qualité pour le stockage et l'utilisation.

**La conception de la base de données** respecte intégralement le RGPD avec des modèles conceptuels et physiques élaborés selon la méthode Merise, incluant la programmation automatisée de l'import des données préparées pour stocker le jeu de données final du projet.

**Le partage du jeu de données** est assuré par des interfaces logicielles et programmables complètes, incluant des APIs REST sécurisées, des schémas de validation, des services de données, et des interfaces frontend, permettant une mise à disposition optimale des données pour le développement du projet.

L'architecture modulaire permet une maintenance facile et une évolution continue du système selon les besoins du projet. 