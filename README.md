# 🔍 EngraveDetect

Application web intelligente pour la détection et l'analyse des gravures nasales sur les verres optiques.

## 📋 Vue d'ensemble

EngraveDetect est une solution complète qui permet aux professionnels de l'optique d'identifier et d'analyser les verres optiques à partir de leurs gravures nasales. Le système combine une interface utilisateur intuitive avec des modèles d'intelligence artificielle avancés pour une identification précise et rapide.

### Architecture du Système

```mermaid
graph TD
    A[Frontend] -->|HTTP/REST| B[API Principale]
    A -->|IA Requests| C[API IA]
    B -->|SQL| D[(Azure SQL)]
    C -->|Modèle IA| E[EfficientNet]
    B -->|Auth| F[JWT Service]
    B -->|Metrics| G[Prometheus]
    G -->|Visualisation| H[Grafana]
```

### Structure du Projet

```mermaid
graph LR
    A[EngraveDetect] --> B[src/]
    B --> C[api/]
    B --> D[api_ia/]
    B --> E[front/]
    B --> F[database/]
    B --> G[models/]
    B --> H[utils/]
    A --> I[data/]
    I --> J[gravures/]
    A --> K[docs/]
    A --> L[tests/]
```

## 🚀 Fonctionnalités Principales

- 🎨 Interface de dessin intuitive pour reproduire les gravures
- 🤖 Modèle IA (EfficientNet) pour la reconnaissance des gravures
- 🏷️ Système de tags pour affiner les recherches
- 📊 Visualisation des résultats avec scores de confiance
- 🔒 Authentification sécurisée (JWT)
- 📈 Monitoring en temps réel (Prometheus/Grafana)

## 🛠️ Technologies Utilisées

### Stack Technique

```mermaid
graph TD
    A[Frontend] -->|HTML5/CSS3/JS| B[Interface Utilisateur]
    C[Backend] -->|FastAPI| D[API REST]
    C -->|SQLAlchemy| E[ORM]
    F[IA] -->|PyTorch| G[Deep Learning]
    F -->|EfficientNet| H[Classification]
    I[Infrastructure] -->|Docker| J[Conteneurisation]
    I -->|Azure SQL| K[Base de données]
    L[Monitoring] -->|Prometheus| M[Métriques]
    L -->|Grafana| N[Dashboards]
```

## 🏗️ Installation

### Prérequis

- Python 3.10+
- Docker et Docker Compose
- Compte Azure (pour la base de données)
- Git

### Configuration

1. **Cloner le repository**
   ```bash
   git clone https://github.com/votre-username/engravedetect-final.git
   cd engravedetect-final
   ```

2. **Créer l'environnement virtuel**
   ```bash
   python -m venv engravedetect-env
   source engravedetect-env/bin/activate  # Linux/Mac
   # ou
   .\engravedetect-env\Scripts\activate  # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration des variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos paramètres
   ```

### Démarrage

```bash
# Lancer avec Docker Compose
docker-compose up --build

# Services disponibles sur :
# - Frontend : http://localhost:80
# - API : http://localhost:8000
# - API IA : http://localhost:8001
# - Prometheus : http://localhost:9090
# - Grafana : http://localhost:3001
```

## 📚 Documentation

### Architecture des Services

```mermaid
flowchart TD
    A[Client] -->|HTTP| B[Frontend Nginx]
    B -->|/api| C[API FastAPI]
    B -->|/api_ia| D[API IA FastAPI]
    C -->|SQL| E[(Azure SQL)]
    D -->|PyTorch| F[Modèle IA]
    C -->|Metrics| G[Prometheus]
    G -->|Visualization| H[Grafana]
```

### Flux de Données

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant F as Frontend
    participant A as API
    participant I as API IA
    participant D as Database

    U->>F: Dessine gravure
    F->>I: Envoie image
    I->>I: Analyse IA
    I->>F: Retourne prédictions
    F->>A: Recherche verres
    A->>D: Query SQL
    D->>A: Résultats
    A->>F: Liste des verres
    F->>U: Affiche résultats
```

## 🧪 Tests

```bash
# Activer l'environnement virtuel
source engravedetect-env/bin/activate

# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src tests/
```

## 🔒 Sécurité

- Authentification JWT avec refresh tokens
- Rate limiting sur les endpoints sensibles
- Validation des entrées utilisateur
- Protection CORS configurée
- Logging sécurisé des accès

## 📈 Monitoring

- Métriques système via Prometheus
- Dashboards Grafana personnalisés
- Alerting configuré
- Logs centralisés

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
- Contacter l'équipe technique : support@engravedetect.com 