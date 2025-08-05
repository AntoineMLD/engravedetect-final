# C9. API d'Intelligence Artificielle

## Table des Matières
- [Contexte et Objectifs](#contexte-et-objectifs)
- [Architecture Technique](#architecture-technique)
  - [Stack Technologique](#stack-technologique)
  - [Organisation du Code](#organisation-du-code)
- [Endpoints de l'API](#endpoints-de-lapi)
  - [Authentification et gestion utilisateur](#authentification-et-gestion-utilisateur)
  - [Données verres](#données-verres)
  - [IA (embedding, matching)](#ia-embedding-matching)
  - [Monitoring et santé](#monitoring-et-santé)
- [Fonctionnalités de l'API](#fonctionnalités-de-lapi)
- [Sécurité](#sécurité)
- [Exemples d'utilisation](#exemples-dutilisation)

---

## Contexte et Objectifs

Le projet EngraveDetect intègre une API d'intelligence artificielle conçue pour la classification et l'analyse d'images de verres optiques, la gestion des comptes utilisateurs et la conformité RGPD. L'API, développée avec FastAPI, offre une interface REST robuste et documentée automatiquement.

---

## Architecture Technique

### Stack Technologique
- **FastAPI** (framework principal, documentation auto)
- **PyTorch** (moteur de deep learning)
- **EfficientNet** (modèle de classification)
- **JWT** (authentification)
- **PostgreSQL** (base de données)
- **python-magic** (validation MIME images)
- **slowapi** (rate limiting)

### Organisation du Code

**Structure des répertoires de l'API IA :**

```bash
src/api_ia/
├── app/
│   ├── main.py            # Point d'entrée et configuration de l'API
│   ├── model_loader.py    # Chargement du modèle
│   ├── security.py        # Sécurité et authentification
│   ├── config.py          # Configuration
│   ├── database.py        # Accès base de données
│   └── ...
├── models/                # Modèles deep learning
└── weights/               # Poids du modèle EfficientNet
```

*Description : Cette structure organise le code en modules logiques avec une séparation claire entre la logique métier (app/), les modèles d'IA et les poids du modèle.*

---

## Endpoints de l'API

### Authentification et gestion utilisateur
- `POST /token` : Connexion, obtention d'un JWT
- `GET /me` : Récupération des données personnelles (username, email)
- `DELETE /me` : Suppression du compte utilisateur (droit à l'oubli RGPD)

### Données verres
- `GET /verre/{verre_id}` : Détails d'un verre
- `GET /verres` : Liste des verres avec filtres

### IA (embedding, matching)
- `POST /embedding` : Calcul d'embedding d'une image (auth requis)
- `POST /match` : Recherche de correspondances IA pour une image (auth requis)
- `POST /search_tags` : Recherche par tags (auth requis)

### Monitoring et santé
- `GET /metrics` : Métriques Prometheus (public)
- `GET /model/health` : Statut de santé du modèle IA (public)

---

## Fonctionnalités de l'API

### 1. Système d'Authentification
- JWT généré à la connexion (`/token`), transmis dans l'en-tête `Authorization: Bearer <token>`
- Clé secrète statique (pas de rotation automatique)
- Pas de gestion de session côté serveur (stateless)
- Mots de passe hashés (bcrypt)
- Expiration des tokens (30 min)

### 2. Classification d'Images et Embedding
- `POST /match` : Analyse d'image, retour des meilleures correspondances
- `POST /embedding` : Extraction de vecteurs d'embedding
- Validation des images (taille, format, type MIME)
- Rate limiting (5 requêtes/minute)

### 3. Gestion RGPD et comptes utilisateurs
- Accès à ses données personnelles (`/me` GET)
- Suppression de compte (`/me` DELETE)
- Politique de confidentialité accessible sur le site

### 4. Monitoring et détection de drift
- Métriques Prometheus en temps réel (`/metrics`)
- Statut de santé du modèle (`/model/health`)
- Détection automatique de drift des données
- Alertes et seuils configurables

---

## Sécurité
- Authentification JWT obligatoire pour toutes les routes sensibles
- Middleware de headers de sécurité (CSP, X-Frame-Options, etc.)
- Pas de CSRF (API REST, pas de cookie/session)
- Validation rigoureuse des entrées (Pydantic, python-magic)
- Logging des accès et des erreurs

---

## Exemples d'utilisation

### Authentification (connexion)

**Commande curl pour s'authentifier :**

```bash
curl -X POST http://localhost:8001/token -d "username=monuser&password=monmdp"
```

*Description : Cette commande envoie les identifiants utilisateur au endpoint /token pour obtenir un token JWT d'authentification.*

### Accès à ses données personnelles
```bash
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8001/me
```

### Suppression de compte
```bash
curl -X DELETE -H "Authorization: Bearer <TOKEN>" http://localhost:8001/me
```

### Classification IA
```bash
curl -X POST http://localhost:8001/match \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@monimage.png"
```

### Embedding IA
```bash
curl -X POST http://localhost:8001/embedding \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@monimage.png"
```

### Monitoring du modèle
```bash
# Métriques Prometheus
curl http://localhost:8001/metrics

# Santé du modèle
curl http://localhost:8001/model/health | jq
```

---

## Documentation
- Documentation interactive Swagger UI : `/docs`
- Documentation ReDoc : `/redoc`
- Schéma OpenAPI : `/openapi.json`

---

## Limitations et TODO
- Pas de rotation automatique de la clé JWT
- Pas de gestion de session côté serveur (stateless)
- Pas de gestion de révocation de token
- Les headers de sécurité sont gérés par middleware, mais peuvent être renforcés
- Les tests de performance et d'intégration sont à compléter

## Documentation Complémentaire
- [Monitoring de l'API IA](C14_Monitoring_API_IA.md) : Architecture de monitoring, métriques, dashboards
- [Détection de Drift](C15_Drift_Detection.md) : Guide complet de la détection de dérives
- [Intégration API IA](C10_Integration_API_IA.md) : Communication entre services
- [Sécurité et Authentification](C16_Securite_Authentification.md) : Règles d'authentification, autorisation et sécurité

---

## Conclusion

L'API IA d'EngraveDetect offre une solution robuste et sécurisée pour l'analyse d'images de verres optiques et la gestion des comptes utilisateurs. La conformité RGPD est assurée par des routes dédiées et une politique de confidentialité accessible. Les axes d'amélioration prioritaires concernent la couverture de tests et le renforcement de la sécurité. 