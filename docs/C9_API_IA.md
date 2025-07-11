# C9. API d'Intelligence Artificielle

## Contexte et Objectifs

Le projet EngraveDetect intègre une API d'intelligence artificielle conçue pour la classification et l'analyse d'images de verres optiques, la gestion des comptes utilisateurs et la conformité RGPD. L'API, développée avec FastAPI, offre une interface REST robuste et documentée automatiquement.

## Architecture Technique

### Stack Technologique
- **FastAPI** (framework principal, documentation auto)
- **PyTorch** (moteur de deep learning)
- **EfficientNet** (modèle de classification)
- **JWT** (authentification)
- **Azure SQL** (base de données)
- **python-magic** (validation MIME images)
- **slowapi** (rate limiting)

### Organisation du Code

```
api_ia/
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

## Endpoints de l'API

### Authentification et gestion utilisateur
- `POST /auth/register` : Inscription (email, username, mot de passe)
- `POST /token` : Connexion, obtention d'un JWT
- `GET /me` : Récupération des données personnelles (username, email)
- `DELETE /me` : Suppression du compte utilisateur (droit à l'oubli RGPD)

### Données verres
- `GET /verre/{verre_id}` : Détails d'un verre
- `GET /verres` : Liste des verres avec filtres

### IA (embedding, matching)
- `POST /embedding` : Calcul d'embedding d'une image (auth requis)
- `POST /match` : Recherche de correspondances IA pour une image (auth requis)

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
- Inscription avec consentement RGPD (case à cocher, lien vers `confidentialite.html`)
- Accès à ses données personnelles (`/me` GET)
- Suppression de compte (`/me` DELETE)
- Politique de confidentialité accessible sur le site

## Sécurité
- Authentification JWT obligatoire pour toutes les routes sensibles
- Middleware de headers de sécurité (CSP, X-Frame-Options, etc.)
- Pas de CSRF (API REST, pas de cookie/session)
- Validation rigoureuse des entrées (Pydantic, python-magic)
- Logging des accès et des erreurs

## Exemples d'utilisation

### Authentification (connexion)
```bash
curl -X POST http://localhost:8001/token -d "username=monuser&password=monmdp"
```

### Inscription
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "monmdp"}'
```

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

## Documentation
- Documentation interactive Swagger UI : `/docs`
- Documentation ReDoc : `/redoc`
- Schéma OpenAPI : `/openapi.json`

## Limitations et TODO
- Pas de rotation automatique de la clé JWT
- Pas de gestion de session côté serveur (stateless)
- Pas de gestion de révocation de token
- Les headers de sécurité sont gérés par middleware, mais peuvent être renforcés
- Les tests de performance et d'intégration sont à compléter

## Conclusion

L'API IA d'EngraveDetect offre une solution robuste et sécurisée pour l'analyse d'images de verres optiques et la gestion des comptes utilisateurs. La conformité RGPD est assurée par des routes dédiées et une politique de confidentialité accessible. Les axes d'amélioration prioritaires concernent la couverture de tests et le renforcement de la sécurité. 