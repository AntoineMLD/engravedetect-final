#  EngraveDetect

Application web intelligente pour la détection et l'analyse des gravures nasales sur les verres optiques.

---

##  Vue d'ensemble

EngraveDetect est une solution complète pour l'identification, l'analyse et la gestion des verres optiques à partir de leurs gravures. Elle combine une interface web moderne, une API sécurisée, des modèles IA performants et une infrastructure cloud robuste.

### Flux de données principal
```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant F as Frontend
    participant A as API
    participant I as API IA
    participant D as Database

    U->>F: Dessin ou upload gravure
    F->>I: Envoie image (POST /match)
    I->>I: Prédiction IA
    I->>F: Résultat (tags, similarité)
    F->>A: Recherche verres (POST /search_tags)
    A->>D: SQL Query
    D->>A: Résultats verres
    A->>F: Liste verres filtrés
    F->>U: Affichage résultats
```

### Structure du projet
```
engravedetect-final/
├── src/
│   ├── api/              # API principale (FastAPI)
│   ├── api_ia/           # API IA (classification, embeddings)
│   ├── front/            # Interface utilisateur
│   ├── data/             # Scripts de traitement des données
│   ├── database/         # Modèles et migrations
│   ├── models/           # Modèles IA
│   ├── orchestrator/     # Pipeline de données
│   ├── scripts/          # Scripts utilitaires
│   └── utils/            # Utilitaires
├── tests/                # Tests automatisés
├── docs/                 # Documentation complète
├── data/                 # Données et images
├── monitoring/           # Configuration monitoring
├── docker-compose.yml    # Orchestration Docker
├── Dockerfile*           # Images Docker
└── requirements*.txt     # Dépendances Python
```

---

##  Démarrage rapide

### Prérequis
- Python 3.12+
- Docker & Docker Compose
- Git
- Compte PostgreSQL (ou SQLite pour le développement)

### Installation & Lancement
1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-username/engravedetect-final.git
   cd engravedetect-final
   ```

2. **Configurer l'environnement**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   .\venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Variables d'environnement**
   - Copie le fichier `.env` fourni (ou crée-le à partir de `.env.example` si présent).
   - Renseigne les accès base de données, clés JWT, etc. **Ne jamais commiter de secrets !**

4. **Lancer l'application**
   ```bash
   docker-compose up --build
   ```
   - Frontend : http://localhost:8080
   - API : http://localhost:8000
   - API IA : http://localhost:8001
   - Prometheus : http://localhost:9090
   - Grafana : http://localhost:3001

---

##  Technologies principales
- **Frontend** : HTML5, CSS3, JavaScript (vanilla)
- **Backend** : Python 3.12, FastAPI, SQLAlchemy
- **IA/ML** : PyTorch, EfficientNet, OpenCV
- **Base de données** : PostgreSQL (production), SQLite (développement)
- **DevOps** : Docker, NGINX, Prometheus, Grafana, GitHub Actions
- **Tests** : Pytest, Playwright (E2E)

---

##  Documentation
La documentation complète est dans le dossier [`docs/`](docs/).

### Fichiers clés :
- [`docs/C1_Automatisation_Extraction_Donnees.md`](docs/C1_Automatisation_Extraction_Donnees.md) : Pipeline d'extraction de données
- [`docs/C3_Agregation_Donnees.md`](docs/C3_Agregation_Donnees.md) : Agrégation et traitement des données
- [`docs/C5_API_REST.md`](docs/C5_API_REST.md) : API REST principale
- [`docs/C9_API_IA.md`](docs/C9_API_IA.md) : API IA
- [`docs/C13_MLOps_Pipeline.md`](docs/C13_MLOps_Pipeline.md) : Pipeline MLOps
- [`docs/C4_Base_Donnees_RGPD.md`](docs/C4_Base_Donnees_RGPD.md) : RGPD & sécurité
- [`docs/PLAYWRIGHT_GUIDE.md`](docs/PLAYWRIGHT_GUIDE.md) : Tests E2E

---

##  Initialisation de la base de données et injection de données

Le build Docker lance les services, mais la base est vide. Suis ces étapes pour initialiser le schéma et insérer des données pour tester l'application.

1. Démarrer PostgreSQL (ou tout le stack)
   ```bash
   docker-compose up -d postgres
   # ou
   docker-compose up --build -d
   ```

2. Configurer la connexion base de données
   - Crée un fichier `.env` à la racine (ou copie depuis `.env.example` si présent)
   - Renseigne `DATABASE_URL` (exemple PostgreSQL local):
     ```
     DATABASE_URL=postgresql+psycopg2://postgres:<motdepasse>@localhost:5432/<nom_bdd>
     ```

3. Créer les tables de l'API (utilisateurs, etc.)
   ```bash
   python -c "from src.api.core.database.init_db import init_db; init_db()"
   ```

4. Créer/réinitialiser les tables données (staging, enhanced, verres)
   ```bash
   python -c "from src.database.reset_database import reset_database; reset_database()"
   ```

5. Remplir la base (choisir une option)
   - Option A • Scraping (insère en staging), puis nettoyage/enrichissement
     ```bash
     # Scraping (Scrapy)
     cd src/data/scraping
     export PYTHONPATH=$(pwd)/../../..
     scrapy crawl glass_spider

     # Nettoyage → enhanced
     cd -
     python -m src.data.processing.cleaner

     # Enrichissement → verres
     python -m src.data.processing.enricher
     ```
   - Option B • Importer depuis un CSV enhanced (si disponible)
     ```bash
     python -m src.data.processing.import_enhanced
     ```

6. Vérifier l'accès API et documentation locale
   - API: http://localhost:8000
   - Swagger: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Via NGINX: `/api` proxifie l'API; préfère l'accès direct sur le port 8000 pour la doc.

---

##  Tests
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer tous les tests
pytest

# Couverture
pytest --cov=src tests/

# Tests spécifiques
pytest tests/api/
pytest tests/test_playwright_e2e.py -v

# Tests E2E avec Playwright
pytest tests/test_playwright_e2e.py --headed
```

---

##  Sécurité & bonnes pratiques
- **Aucun secret ne doit être commité** : utilise `.env` (jamais versionné) pour toutes les clés, tokens, accès base de données, etc.
- **CSP stricte** : la configuration NGINX applique une politique CSP sécurisée.
- **Authentification JWT** : toutes les routes sensibles sont protégées.
- **Headers de sécurité** : configuration sécurisée dans l'API.
- **Conformité RGPD** : gestion des données personnelles et droit à l'oubli.

---

##  Contribution
1. Fork le projet
2. Crée une branche (`git checkout -b feature/ma-feature`)
3. Commit tes changements (`git commit -m 'feat: ma feature'`)
4. Push sur ta branche (`git push origin feature/ma-feature`)
5. Ouvre une Pull Request

---

##  Licence
Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

##  Support
Pour toute question ou problème :
- Ouvre une issue sur GitHub
- Consulte la documentation dans le dossier `docs/`

---

##  Remerciements
- Tous les contributeurs
- La communauté open source
- Nos partenaires et clients
