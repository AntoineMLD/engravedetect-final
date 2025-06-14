# 💾 Base de Données EngraveDetect

Gestion de la base de données Azure SQL pour le stockage et l'analyse des données de verres optiques.

## 📋 Fonctionnalités

- 💾 Stockage structuré des données
- 🔄 Migrations automatisées
- 📊 Requêtes optimisées
- 🔒 Gestion des connexions
- 📈 Monitoring des performances

## 🏗️ Structure

```
database/
├── models/          # Modèles SQLAlchemy
├── migrations/      # Scripts de migration
├── queries/         # Requêtes complexes
└── utils/          # Utilitaires DB
```

## 🚀 Démarrage

1. **Configuration Azure**
   ```bash
   # Créer une base de données Azure SQL
   az sql server create --name engravedetect-db --resource-group engravedetect-rg
   az sql db create --name engravedetect --server engravedetect-db
   ```

2. **Configuration locale**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos paramètres Azure
   ```

3. **Initialiser la base**
   ```bash
   alembic upgrade head
   ```

## 📊 Schéma de la Base

### Tables Principales
- `verres` : Données des verres
- `fournisseurs` : Liste des fournisseurs
- `materiaux` : Types de matériaux


### Relations
- Un verre appartient à un fournisseur
- Un verre a un matériau
- Un verre appartient à une gamme

## 🔄 Migrations

```bash
# Créer une migration
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

## 🧪 Tests

```bash
# Tests de la base de données
pytest tests/database/

# Tests de performance
python -m src.database.tests.benchmark
```

## 📝 Documentation

- [Guide de migration](docs/DB_MIGRATION.md)
- [Schéma de la base](docs/DB_SCHEMA.md)
- [Guide d'optimisation](docs/DB_OPTIMIZATION.md)

## 🔒 Sécurité

- Chiffrement des données sensibles
- Gestion des accès
- Audit des opérations
- Sauvegardes automatiques

## 📈 Performance

- Indexation optimisée
- Requêtes préparées
- Mise en cache
- Pool de connexions

## 🔧 Maintenance

- Nettoyage des données
- Optimisation des index
- Mise à jour des statistiques
- Vérification de l'intégrité

## 🐛 Débogage

- Logs de requêtes
- Métriques de performance
- Traces d'erreurs
- Monitoring en temps réel

## 📚 Ressources

- [Documentation Azure SQL](https://docs.microsoft.com/azure/sql-database/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)
- [Guide Alembic](https://alembic.sqlalchemy.org/) 