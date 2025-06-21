# 🎯 EngraveDetect

Système intelligent de gestion et d'analyse de données optiques, spécialisé dans la détection et l'analyse des gravures nasales des verres optiques.

## 📋 Fonctionnalités Principales

- 🔍 Détection automatique des caractéristiques des verres
- 📊 Analyse et classification des gravures nasales
- 💾 Stockage structuré dans Azure SQL
- 🔄 Pipeline de traitement automatisé
- 🔒 API REST sécurisée avec FastAPI
- 📱 Interface utilisateur intuitive

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.10+
- Docker et Docker Compose
- Compte Azure (pour la base de données)
- Git

### Installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/votre-username/engravedetect-final.git
   cd engravedetect-final
   ```

2. **Configuration de l'environnement**
   ```bash
   # Créer l'environnement virtuel
   python -m venv venv
   
   # Activer l'environnement
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   # Installer les dépendances
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configuration des variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos paramètres
   ```

4. **Lancer avec Docker**
   ```bash
   docker-compose up --build
   ```

## 🏗️ Structure du Projet

```
engravedetect/
├── src/                    # Code source principal
│   ├── api/               # API FastAPI
│   ├── api_ia/            # Services IA
│   ├── database/          # Gestion de la base de données
│   ├── models/            # Modèles de données
│   ├── orchestrator/      # Orchestration du pipeline
│   └── utils/             # Utilitaires communs
├── tests/                 # Tests unitaires et d'intégration
├── docs/                  # Documentation
├── scripts/               # Scripts utilitaires
└── data/                  # Données et ressources
```

## 🛠️ Technologies Utilisées

- **Backend**: Python, FastAPI
- **Base de données**: Azure SQL
- **IA/ML**: TensorFlow, OpenCV
- **DevOps**: Docker, GitHub Actions
- **Tests**: Pytest, Coverage

## 📚 Documentation

- [Documentation API](docs/API.md)
- [Guide de Contribution](docs/CONTRIBUTING.md)
- [Architecture Technique](docs/ARCHITECTURE.md)
- [Guide de Déploiement](docs/DEPLOYMENT.md)

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src tests/

# Tests spécifiques
pytest tests/api/
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de support : support@engravedetect.com

## 🙏 Remerciements

- Tous les contributeurs
- La communauté open source
- Nos partenaires et clients 