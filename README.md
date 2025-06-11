# EngraveDetect

Système de gestion et d'analyse de données optiques. Ce projet permet de collecter, traiter et analyser les données de verres optiques, notamment les gravures nasales et les caractéristiques techniques.

## Fonctionnalités

- Scraping automatisé des données de verres optiques
- Nettoyage et standardisation des données
- Stockage structuré dans une base de données Azure SQL
- Détection automatique des caractéristiques des verres :
  - Gamme (Standard, Premium, etc.)
  - Série et niveau
  - Hauteurs minimales et maximales
  - Traitements (Protection, Photochromique)
  - Matériaux et indices

## Structure du Projet

```
engravedetect/
├── src/                           # Code source principal
│   ├── data/                      # Gestion des données
│   │   ├── scraping/             # Scripts de scraping
│   │   │   └── france_optique/   # Spider pour France Optique
│   │   ├── processing/           # Traitement des données
│   │   │   └── cleaner.py        # Nettoyage des données
│   │   └── export/               # Export des données
│   │       └── csv_export.py     # Export vers CSV
│   ├── database/                 # Gestion de la base de données
│   │   └── models/              # Modèles de données
│   │       └── tables.py        # Définition des tables
│   ├── orchestrator/            # Orchestration du pipeline
│   │   └── pipeline_manager.py  # Gestionnaire de pipeline
│   └── utils/                   # Utilitaires communs
├── tests/                       # Tests unitaires
│   └── utils/                  # Tests des utilitaires
├── data/                        # Données exportées
├── logs/                        # Logs d'exécution
├── scripts/                     # Scripts utilitaires
│   └── run_spiders.py         # Lancement des spiders
└── .env                        # Configuration
```

## Structure de la Base de Données

### Tables Principales

- `verres` : Table principale des verres
  - `id` : Identifiant unique
  - `nom` : Nom du verre
  - `variante` : Type de variante (STANDARD, COURT)
  - `hauteur_min` : Hauteur minimale en mm (14mm standard, 11mm court)
  - `hauteur_max` : Hauteur maximale en mm (14mm standard, 11mm court)
  - `indice` : Indice de réfraction
  - `gravure` : Code de gravure nasale
  - `protection` : Présence de protection (UV, Blue)
  - `photochromic` : Verre photochromique
  - Relations avec les tables de référence

### Tables de Référence

- `fournisseurs` : Liste des fournisseurs
- `materiaux` : Types de matériaux
- `gammes` : Gammes de produits
- `series` : Séries et leurs caractéristiques

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
- Copier `.env.example` vers `.env`
- Remplir les informations suivantes :
  ```
  AZURE_SERVER=votre_serveur.database.windows.net
  AZURE_DATABASE=nom_base
  AZURE_USERNAME=utilisateur
  AZURE_PASSWORD=mot_de_passe
  ```

## Utilisation

1. Lancer le scraping des données :
```bash
python -m src.data.scraping.france_optique.run_spiders
```

2. Nettoyer et traiter les données :
```bash
python -m src.data.processing.cleaner
```

3. Créer et remplir les tables :
```bash
python -m src.database.models.tables
```

## Valeurs par Défaut

Le système utilise les valeurs par défaut suivantes :
- Gamme : "STANDARD"
- Série : "INCONNU"
- Variante : "STANDARD"
- Hauteur : 14mm (11mm pour les verres courts)
- Protection : "NON"
- Photochromic : "NON"
- Matériau : "ORGANIQUE"
- Indice : 1.5
- Fournisseur : "INCONNU"

## Maintenance

Pour mettre à jour la base de données :
1. Les nouvelles données sont d'abord stockées dans la table `staging`
2. Puis nettoyées et enrichies dans la table `enhanced`
3. Enfin importées dans les tables finales avec les relations appropriées 

## Pipeline d'Exécution

Le projet utilise un orchestrateur centralisé qui gère l'ensemble du pipeline de données. Voici les étapes principales :

1. **Initialisation**
   - Vérification de la configuration
   - Création des dossiers nécessaires
   - Configuration des logs

2. **Pipeline de Données**
   ```python
   python -m src.orchestrator.pipeline_manager
   ```
   
   Le pipeline exécute séquentiellement :
   - Scraping des données sources
   - Nettoyage et enrichissement
   - Import dans la base de données
   - Export des résultats

3. **Système de Logs**
   - Les logs sont stockés dans le dossier `logs/`
   - Format : `YYYY-MM-DD_pipeline.log`
   - Niveaux de logs :
     - INFO : Progression normale
     - WARNING : Problèmes non critiques
     - ERROR : Erreurs nécessitant attention
     - DEBUG : Détails d'exécution

4. **Gestion des Erreurs**
   - Reprise automatique en cas d'erreur non critique
   - Sauvegarde de l'état en cas d'interruption
   - Notification des erreurs critiques

## Exemple de Log

```log
2024-01-20 10:15:23 INFO     Démarrage du pipeline
2024-01-20 10:15:24 INFO     ✅ Configuration chargée
2024-01-20 10:15:25 INFO     🕷️ Lancement du scraping
2024-01-20 10:20:15 INFO     ✅ Scraping terminé : 150 verres collectés
2024-01-20 10:20:16 INFO     🧹 Début du nettoyage des données
2024-01-20 10:21:00 WARNING  ⚠️ 3 entrées avec indices manquants
2024-01-20 10:21:01 INFO     ✅ Nettoyage terminé
2024-01-20 10:21:02 INFO     💾 Import dans la base de données
2024-01-20 10:22:00 INFO     ✅ Pipeline terminé avec succès
``` 