# C16. Sécurité, Authentification et Autorisation - API IA

## Table des Matières
- [Contexte et Objectifs](#contexte-et-objectifs)
- [Architecture de Sécurité](#architecture-de-sécurité)
  - [Stack de Sécurité](#stack-de-sécurité)
  - [Flux d'Authentification](#flux-dauthentification)
- [Authentification JWT](#authentification-jwt)
  - [Génération de Token](#génération-de-token)
  - [Structure du Token JWT](#structure-du-token-jwt)
  - [Validation du Token](#validation-du-token)
- [Autorisation et Règles d'Accès](#autorisation-et-règles-daccès)
- [Gestion des Erreurs](#gestion-des-erreurs)
- [Validation des Entrées](#validation-des-entrées)
- [Rate Limiting](#rate-limiting)
- [Audit et Logging](#audit-et-logging)
- [Middleware de Sécurité](#middleware-de-sécurité)
- [Bonnes Pratiques](#bonnes-pratiques)
- [Tests de Sécurité](#tests-de-sécurité)
- [Monitoring de Sécurité](#monitoring-de-sécurité)
- [Dépannage](#dépannage)
- [Évolutions Futures](#évolutions-futures)

---

## Contexte et Objectifs

Ce document détaille les mécanismes de sécurité, d'authentification et d'autorisation de l'API IA EngraveDetect. Il couvre les règles d'accès, la gestion des erreurs, l'audit et les bonnes pratiques de sécurité.

---

## Architecture de Sécurité

### Stack de Sécurité
- **JWT** : Authentification stateless
- **bcrypt** : Hachage des mots de passe
- **python-magic** : Validation des fichiers
- **slowapi** : Rate limiting
- **Middleware** : Headers de sécurité

### Flux d'Authentification

**Diagramme du processus d'authentification :**

```mermaid
graph LR
    A[Client] --> B[/token POST]
    B --> C[Validation DB + Hash]
    C --> D[JWT Token]
    
    A1[Username/Password] --> B
    B1[OAuth2Password RequestForm] --> C
    C1[bcrypt.verify() + DB Query] --> D
    D1[JWT.encode() + Expiration] --> D
```

*Description : Le flux d'authentification commence par l'envoi des identifiants par le client, suivi de la validation en base de données avec vérification du hash, puis génération d'un token JWT avec expiration.*

---

## Authentification JWT

### Génération de Token

#### Endpoint : `POST /token`
```bash
curl -X POST http://localhost:8001/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=monuser&password=monmdp"
```

#### Réponse Succès (200)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "version": "1"
}
```

#### Réponse Erreur (401)
```json
{
  "detail": "Incorrect username or password"
}
```

### Structure du Token JWT

#### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

#### Payload
```json
{
  "sub": "username",
  "exp": 1754379409,
  "iat": 1754377609
}
```

#### Signature
- **Algorithme** : HS256
- **Clé secrète** : `SECRET_KEY` (variable d'environnement)
- **Expiration** : 30 minutes par défaut

### Validation du Token

#### Processus de Vérification
1. **Extraction** : Header `Authorization: Bearer <token>`
2. **Décodage** : Vérification signature avec `SECRET_KEY`
3. **Expiration** : Vérification du timestamp `exp`
4. **Utilisateur** : Vérification existence en base de données
5. **Logging** : Enregistrement de l'accès

#### Code de Validation
```python
def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
```

---

## Règles d'Autorisation

### Endpoints par Niveau d'Accès

#### 🔓 **Public (Aucune authentification)**
- `GET /` : Message d'accueil
- `GET /health` : Statut de santé
- `GET /metrics` : Métriques Prometheus
- `GET /model/health` : Santé du modèle IA

#### 🔐 **Authentification Requise**
- `POST /token` : Connexion (username/password)
- `GET /me` : Données personnelles utilisateur
- `DELETE /me` : Suppression de compte (RGPD)
- `GET /verre/{id}` : Détails d'un verre
- `GET /verres` : Liste des verres
- `POST /embedding` : Calcul d'embedding
- `POST /match` : Recherche de correspondances
- `POST /search_tags` : Recherche par tags

### Matrice d'Autorisation

| Endpoint | Méthode | Authentification | Rate Limit | Validation |
|----------|---------|------------------|------------|------------|
| `/token` | POST | ❌ (connexion) | 10/min | Username/Password |
| `/me` | GET | ✅ JWT | 20/min | Token valide |
| `/me` | DELETE | ✅ JWT | 5/min | Token valide |
| `/embedding` | POST | ✅ JWT | 5/min | Token + Image |
| `/match` | POST | ✅ JWT | 5/min | Token + Image |
| `/search_tags` | POST | ✅ JWT | 10/min | Token + JSON |
| `/verre/{id}` | GET | ✅ JWT | 20/min | Token + ID |
| `/metrics` | GET | ❌ Public | 60/min | Aucune |

---

## Gestion des Erreurs d'Authentification

### Codes d'Erreur HTTP

#### 401 Unauthorized
```json
{
  "detail": "Invalid authentication"
}
```
**Causes :**
- Token manquant
- Token invalide (signature incorrecte)
- Token expiré
- Utilisateur non trouvé en base

#### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```
**Causes :**
- Rate limit dépassé
- Fichier trop volumineux
- Type de fichier non autorisé

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Causes :**
- Champs manquants dans le formulaire
- Format de données incorrect

### Exemples d'Erreurs Courantes

#### Token Expiré
```bash
curl -H "Authorization: Bearer expired_token" \
  http://localhost:8001/me
```
```json
{
  "detail": "Invalid authentication"
}
```

#### Rate Limit Dépassé
```bash
# Après 5 requêtes en 1 minute
curl -X POST http://localhost:8001/embedding \
  -H "Authorization: Bearer valid_token" \
  -F "file=@image.jpg"
```
```json
{
  "detail": "Too many requests"
}
```

#### Fichier Invalide
```bash
curl -X POST http://localhost:8001/match \
  -H "Authorization: Bearer valid_token" \
  -F "file=@document.pdf"
```
```json
{
  "detail": "Invalid file type"
}
```

---

## Validation des Entrées

### Validation des Images

#### Critères de Validation
```python
def validate_image_file(file_content: bytes, filename: Optional[str] = None) -> bool:
    # Type MIME
    mime_type = magic.from_buffer(file_content, mime=True)
    if not mime_type.startswith("image/"):
        return False
    
    # Extension (si filename fourni)
    if filename:
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
        file_extension = os.path.splitext(filename.lower())[1]
        if file_extension not in allowed_extensions:
            return False
    
    # Taille (max 10MB)
    if len(file_content) > 10 * 1024 * 1024:
        return False
    
    return True
```

#### Types de Fichiers Autorisés
- **Images** : JPG, JPEG, PNG, GIF, BMP
- **Taille max** : 10 MB
- **Validation** : MIME type + extension + taille

### Validation des Données JSON

#### Schéma Pydantic
```python
class UserLogin(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
```

---

## Rate Limiting

### Configuration par Endpoint

#### Endpoints Sensibles (5/min)
- `POST /embedding` : Calcul d'embedding
- `POST /match` : Recherche de correspondances

#### Endpoints Modérés (10/min)
- `POST /token` : Connexion
- `POST /search_tags` : Recherche par tags

#### Endpoints Standard (20/min)
- `GET /me` : Données personnelles
- `GET /verre/{id}` : Détails verre

#### Endpoints Publics (60/min)
- `GET /metrics` : Métriques Prometheus

### Implémentation
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/embedding")
@limiter.limit("5/minute")
async def get_image_embedding(request: Request, ...):
    # Endpoint avec rate limiting
```

---

## Audit et Logging

### Logs de Sécurité

#### Configuration
```python
def setup_security_logging():
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    
    # Handler avec rotation
    file_handler = RotatingFileHandler(
        "logs/security.log", 
        maxBytes=1024*1024, 
        backupCount=5
    )
    
    return security_logger
```

#### Types d'Événements Loggés

##### 🔐 Authentification
```python
# Connexion réussie
log_security_event("login_success", f"Connexion réussie pour {username}", username)

# Connexion échouée
log_security_event("login_failed", f"Tentative échouée pour {username}", username)

# Token créé
log_security_event("TOKEN_CREATED", f"Token for {username}")
```

##### 🚫 Accès Refusés
```python
# Token invalide
log_security_event("invalid_token", "Token invalide fourni")

# Rate limit dépassé
log_security_event("rate_limit_exceeded", f"Rate limit pour {username}")

# Fichier invalide
log_security_event("file_upload_error", "Fichier invalide uploadé")
```

##### 👤 Gestion Comptes
```python
# Compte supprimé
log_security_event("account_deleted", f"Compte supprimé: {username}")

# Données RGPD consultées
log_security_event("rgpd_data_access", f"Données RGPD consultées: {username}")
```

### Format des Logs
```
2025-08-05 10:30:15 - security - INFO - Connexion réussie pour l'utilisateur admin
2025-08-05 10:30:20 - security - WARNING - Tentative de connexion échouée pour l'utilisateur hacker
2025-08-05 10:30:25 - security - INFO - Token créé pour l'utilisateur user123
```

---

## Middleware de Sécurité

### Headers de Sécurité

#### Configuration
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Headers de sécurité
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response
```

#### Headers Appliqués
- **X-Content-Type-Options** : `nosniff` (prévention MIME sniffing)
- **X-Frame-Options** : `DENY` (prévention clickjacking)
- **X-XSS-Protection** : `1; mode=block` (protection XSS)
- **Strict-Transport-Security** : `max-age=31536000` (HTTPS obligatoire)
- **Content-Security-Policy** : `default-src 'self'` (CSP)

---

## Bonnes Pratiques de Sécurité

### 1. Gestion des Mots de Passe
- ✅ **Hachage** : bcrypt avec salt automatique
- ✅ **Complexité** : Validation côté client
- ✅ **Stockage** : Jamais en clair en base

### 2. Gestion des Tokens
- ✅ **Expiration** : 30 minutes par défaut
- ✅ **Stateless** : Pas de session côté serveur
- ✅ **Signature** : HS256 avec clé secrète

### 3. Validation des Entrées
- ✅ **Images** : Type MIME + extension + taille
- ✅ **JSON** : Schémas Pydantic
- ✅ **Sanitisation** : Échappement automatique

### 4. Rate Limiting
- ✅ **Par endpoint** : Limites adaptées
- ✅ **Par IP** : Prévention d'abus
- ✅ **Logging** : Traçabilité des abus

### 5. Logging et Audit
- ✅ **Rotation** : Logs avec rotation automatique
- ✅ **Séparation** : Logs de sécurité séparés
- ✅ **Traçabilité** : Tous les événements loggés

---

## Tests de Sécurité

### Tests d'Authentification

#### Test Token Valide
```python
def test_valid_token_access(client, user_token):
    token, username, _ = user_token
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```

#### Test Token Expiré
```python
def test_expired_token_access(client):
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    response = client.get("/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
```

#### Test Token Manquant
```python
def test_missing_token_access(client):
    response = client.get("/me")
    assert response.status_code == 401
```

### Tests de Sécurité

#### Tests existants dans le projet
```python
# Tests d'authentification dans tests/test_routes/test_model_monitoring.py
def test_valid_token_access(client, user_token):
    token, username, _ = user_token
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_expired_token_access(client):
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    response = client.get("/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
```

**Note** : Les tests de rate limiting et de validation de fichiers ne sont pas encore implémentés dans le projet.

---

## Monitoring de Sécurité

### Métriques de Sécurité

#### Prometheus Metrics
```python
# Métriques existantes dans main.py
MATCH_REQUEST_COUNT = Counter("match_requests_total", "Total /match requests")
MATCH_REQUEST_ERRORS = Counter("match_request_errors_total", "Errors in /match requests")
MATCH_LATENCY = Histogram("match_latency_seconds", "Latency for /match")

EMBED_REQUEST_COUNT = Counter("embedding_requests_total", "Total /embedding requests")
EMBED_REQUEST_ERRORS = Counter("embedding_request_errors_total", "Errors in /embedding requests")
EMBED_LATENCY = Histogram("embedding_latency_seconds", "Latency for /embedding")

SEARCH_TAGS_COUNT = Counter("search_tags_requests_total", "Total /search_tags requests")
SEARCH_TAGS_ERRORS = Counter("search_tags_errors_total", "Errors in /search_tags")
SEARCH_TAGS_LATENCY = Histogram("search_tags_latency_seconds", "Latency for /search_tags")

VERRE_DETAIL_COUNT = Counter("verre_details_requests_total", "Total /verre/{id} requests")
VERRE_DETAIL_ERRORS = Counter("verre_details_errors_total", "Errors in /verre/{id}")
VERRE_DETAIL_LATENCY = Histogram("verre_details_latency_seconds", "Latency for /verre/{id}")
```

### Alertes de Sécurité

#### Alertes Prometheus existantes
```yaml
# Alertes définies dans monitoring/prometheus/model_alerts.yml
- alert: ModelTop1AccuracyDegradation
  expr: model_top1_accuracy < 0.8
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Dégradation de l'accuracy Top-1"
    description: "L'accuracy Top-1 est tombée en dessous de 80%"

- alert: ModelTop3AccuracyDegradation
  expr: model_top3_accuracy < 0.9
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Dégradation de l'accuracy Top-3"
    description: "L'accuracy Top-3 est tombée en dessous de 90%"

- alert: ModelRejectionRateHigh
  expr: model_rejection_rate > 0.2
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Taux de rejet élevé"
    description: "Le taux de rejet a dépassé 20%"
```

---

## Dépannage

### Problèmes Courants

#### 1. Token Expiré
**Symptôme** : `401 Invalid authentication`
**Solution** : Obtenir un nouveau token via `/token`

#### 2. Rate Limit Dépassé
**Symptôme** : `429 Too many requests`
**Solution** : Attendre la fin de la période de limitation

#### 3. Fichier Trop Volumineux
**Symptôme** : `413 Payload too large`
**Solution** : Réduire la taille du fichier (< 10MB)

#### 4. Type de Fichier Non Autorisé
**Symptôme** : `400 Invalid file type`
**Solution** : Utiliser un format d'image supporté

### Logs de Debug
```bash
# Vérifier les logs de sécurité
tail -f logs/security.log

# Vérifier les métriques de sécurité
curl http://localhost:8001/metrics | grep security_

# Vérifier la santé de l'API
curl http://localhost:8001/health
```

---

## Évolutions Futures

### Améliorations Possibles

#### 1. Rotation des Clés JWT
- Rotation automatique de `SECRET_KEY`
- Gestion des tokens en cours de validité
- Migration transparente

#### 2. Révocation de Tokens
- Blacklist de tokens révoqués
- Endpoint de révocation
- Synchronisation multi-instances

#### 3. Authentification Multi-Facteurs
- Support TOTP (Time-based One-Time Password)
- Authentification par email/SMS
- Backup codes

#### 4. Audit Avancé
- Logs structurés (JSON)
- Intégration SIEM
- Alertes en temps réel

**Note** : Ces fonctionnalités ne sont pas encore implémentées dans le projet actuel.

---

## Conclusion

L'API IA EngraveDetect implémente une sécurité robuste basée sur JWT avec validation stricte des entrées, rate limiting et audit complet. Les mécanismes de sécurité couvrent l'authentification, l'autorisation et la protection contre les abus.

Les bonnes pratiques de sécurité sont respectées et le système est prêt pour la production avec des possibilités d'évolution vers des mécanismes plus avancés selon les besoins. 