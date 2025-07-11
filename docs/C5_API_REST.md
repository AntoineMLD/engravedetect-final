# C5. API REST pour l'Accès aux Données et l'IA

## Contexte
Ce document décrit l'API REST du projet EngraveDetect, développée avec FastAPI. L'API permet l'accès sécurisé aux données des verres optiques, la gestion des comptes utilisateurs, et l'accès aux fonctionnalités d'IA (embedding, matching). L'authentification se fait par JWT.

## 1. Documentation Technique de l'API

### 1.1 Points de Terminaison (Endpoints)

#### Authentification et gestion utilisateur
```python
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Obtient un token JWT en échange des identifiants."""
    ...

@app.post("/auth/register")
async def register(user: UserCreate):
    """Inscription d'un nouvel utilisateur (email, username, mot de passe)."""
    ...

@app.get("/me")
async def get_me(current_user: str = Depends(get_current_user)):
    """Retourne les données personnelles de l'utilisateur authentifié (username, email)."""
    ...

@app.delete("/me")
async def delete_me(current_user: str = Depends(get_current_user)):
    """Supprime le compte de l'utilisateur authentifié (droit à l'oubli RGPD)."""
    ...
```

#### Endpoints Données Verres
```python
@app.get("/verre/{verre_id}")
async def get_verre(verre_id: int, current_user: str = Depends(get_current_user)):
    """Détails d'un verre par son ID."""
    ...

@app.get("/verres")
async def get_verres(...):
    """Liste des verres avec filtres optionnels."""
    ...
```

#### Endpoints IA (Embedding, Matching)
```python
@app.post("/embedding")
async def get_image_embedding(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    """Retourne l'embedding d'une image de gravure (auth requis)."""
    ...

@app.post("/match")
async def get_best_match(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    """Retourne les meilleures correspondances IA pour une image (auth requis)."""
    ...
```

### 1.2 Authentification JWT
- Authentification obligatoire pour toutes les routes sensibles.
- Le token JWT est généré à la connexion et doit être envoyé dans l'en-tête `Authorization: Bearer <token>`.
- **Note** : Il n'y a pas de gestion de révocation de token en base, seule la validité (signature, expiration) est vérifiée.

### 1.3 Standards OpenAPI
- Documentation automatique générée par FastAPI (`/docs`)
- Schémas de validation avec Pydantic
- Réponses typées et gestion des erreurs standardisée

## 2. Fonctionnalités de l'API

### 2.1 Accès aux Données
- Récupération de la liste des verres avec filtres
- Accès aux détails d'un verre spécifique
- Pagination et filtrage

### 2.2 Gestion des Comptes Utilisateurs et RGPD
- Inscription, connexion, récupération/suppression de ses données personnelles
- Consentement RGPD obligatoire à l'inscription (géré côté frontend)
- Suppression effective du compte à la demande de l'utilisateur

### 2.3 Fonctionnalités IA
- Calcul d'embedding d'image de gravure (`/embedding`)
- Recherche de correspondances IA (`/match`)

### 2.4 Sécurité
- Authentification JWT obligatoire
- Validation des tokens (signature, expiration)
- Protection contre les accès non autorisés

### 2.5 Tests
```python
def test_get_me_ok(client, user_token):
    token, username, email = user_token
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == username
    assert data["email"] == email

def test_delete_me_ok(client, user_token):
    token, username, _ = user_token
    resp = client.delete("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    resp2 = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code in (401, 404)

def test_get_verres(client, auth_headers, test_verre):
    response = client.get("/verres", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
```

## Conclusion

L'API REST du projet EngraveDetect permet un accès sécurisé et contrôlé aux données des verres optiques, à la gestion des comptes utilisateurs, et aux fonctionnalités d'IA. La documentation suit les standards FastAPI/OpenAPI, et la sécurité est assurée par JWT. Les routes RGPD et IA sont bien présentes et testées.

### Points Forts
1. API REST et IA complète et documentée
2. Authentification JWT robuste
3. Gestion RGPD utilisateur (accès/suppression)
4. Filtrage et pagination des données
5. Documentation automatique FastAPI
6. Tests automatisés couvrant les routes critiques 