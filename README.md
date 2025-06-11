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
│   └── utils/                   # Utilitaires communs
├── tests/                       # Tests unitaires
│   └── utils/                  # Tests des utilitaires
├── data/                        # Données exportées
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