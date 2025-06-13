# Documentation API BDD Verres Optiques

## Table des matières
- [Introduction](#introduction)
- [Configuration](#configuration)
- [Authentification](#authentification)
- [Endpoints](#endpoints)
- [Modèles de données](#modèles-de-données)
- [Exemples d'utilisation](#exemples-dutilisation)

## Introduction

Cette API REST permet la gestion des données de verres optiques. Elle est construite avec FastAPI et utilise une base de données SQL Server pour le stockage des données.

### Technologies utilisées
- FastAPI (framework API)
- SQL Server (base de données)
- PyODBC (connecteur base de données)
- Pydantic (validation des données)
- JWT (authentification)

## Configuration

### Variables d'environnement requises

```env
DATABASE_URL=mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+18+for+SQL+Server
SECRET_KEY=votre_clé_secrète
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Configuration Docker

L'API est conteneurisée avec Docker et utilise docker-compose pour orchestrer les services :
- `api_bdd` : Service API FastAPI
- `sql_server` : Base de données SQL Server

## Authentification

L'API utilise l'authentification JWT (JSON Web Token).

### Obtenir un token

```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password
```

Réponse :
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

### Utiliser le token

Inclure le token dans le header `Authorization` :
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Endpoints

### Verres

#### Liste des verres
```http
GET /api/v1/verres
```

Paramètres de requête :
- `skip` (int, optionnel): Nombre d'éléments à sauter
- `limit` (int, optionnel): Nombre maximum d'éléments à retourner
- `fournisseur` (str, optionnel): Filtrer par fournisseur
- `materiau` (str, optionnel): Filtrer par matériau
- `indice` (float, optionnel): Filtrer par indice

Réponse :
```json
{
    "items": [
        {
            "id": 1,
            "nom": "Verre Premium",
            "variante": "STANDARD",
            "hauteur_min": 14,
            "hauteur_max": 14,
            "indice": 1.5,
            "gravure": "ABC123",
            "protection": true,
            "photochromic": false,
            "fournisseur": {
                "id": 1,
                "nom": "Fournisseur A"
            },
            "materiau": {
                "id": 1,
                "nom": "ORGANIQUE"
            }
        }
    ],
    "total": 100
}
```

#### Détails d'un verre
```http
GET /api/v1/verres/{verre_id}
```

Réponse :
```json
{
    "id": 1,
    "nom": "Verre Premium",
    "variante": "STANDARD",
    "hauteur_min": 14,
    "hauteur_max": 14,
    "indice": 1.5,
    "gravure": "ABC123",
    "protection": true,
    "photochromic": false,
    "fournisseur": {
        "id": 1,
        "nom": "Fournisseur A"
    },
    "materiau": {
        "id": 1,
        "nom": "ORGANIQUE"
    }
}
```

### Fournisseurs

#### Liste des fournisseurs
```http
GET /api/v1/verres/fournisseurs/list
```

Réponse :
```json
[
    {
        "id": 1,
        "nom": "Fournisseur A"
    },
    {
        "id": 2,
        "nom": "Fournisseur B"
    }
]
```

### Matériaux

#### Liste des matériaux
```http
GET /api/v1/verres/materiaux/list
```

Réponse :
```json
[
    {
        "id": 1,
        "nom": "ORGANIQUE"
    },
    {
        "id": 2,
        "nom": "MINERAL"
    }
]
```

## Modèles de données

### Verre
```python
class Verre(BaseModel):
    id: int
    nom: str
    variante: str
    hauteur_min: float
    hauteur_max: float
    indice: float
    gravure: str
    protection: bool
    photochromic: bool
    fournisseur_id: int
    materiau_id: int
```

### Fournisseur
```python
class Fournisseur(BaseModel):
    id: int
    nom: str
```

### Matériau
```python
class Materiau(BaseModel):
    id: int
    nom: str
```

## Exemples d'utilisation

### Authentification et récupération des verres

```python
import requests

# Authentification
auth_response = requests.post(
    "http://localhost:8000/api/v1/auth/token",
    data={"username": "user@example.com", "password": "password"}
)
token = auth_response.json()["access_token"]

# Récupération des verres
headers = {"Authorization": f"Bearer {token}"}
verres_response = requests.get(
    "http://localhost:8000/api/v1/verres",
    headers=headers,
    params={"fournisseur": "Fournisseur A", "limit": 10}
)
verres = verres_response.json()
```

### Filtrage des verres par matériau et indice

```python
# Récupérer tous les verres organiques d'indice 1.5
verres_filtres = requests.get(
    "http://localhost:8000/api/v1/verres",
    headers=headers,
    params={
        "materiau": "ORGANIQUE",
        "indice": 1.5
    }
)
```

## Codes d'erreur

- `400 Bad Request`: Requête invalide
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Ressource non trouvée
- `422 Unprocessable Entity`: Données invalides
- `500 Internal Server Error`: Erreur serveur.

## Notes importantes

1. Tous les endpoints nécessitent une authentification JWT valide.
2. Les requêtes de liste supportent la pagination via les paramètres `skip` et `limit`.
3. Les filtres sont optionnels et peuvent être combinés.
4. Les dates sont au format ISO 8601.
5. Les réponses sont en JSON.

## Sécurité

- Utilisation de HTTPS en production
- Tokens JWT avec expiration
- Validation des données avec Pydantic
- Protection contre les injections SQL via SQLAlchemy 



