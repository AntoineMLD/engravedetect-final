# C5. API REST pour l'Accès aux Données

## Contexte
Ce document analyse l'implémentation de l'API REST dans le projet EngraveDetect, qui permet l'accès sécurisé aux données des verres optiques. L'API est développée avec FastAPI et utilise JWT pour l'authentification.

## 1. Documentation Technique de l'API

### 1.1 Points de Terminaison

#### Endpoints d'Authentification
```python
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur.
    - email: Email unique de l'utilisateur
    - username: Nom d'utilisateur unique
    - password: Mot de passe (sera haché)
    """
    return auth_service.create_user(db, user)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Obtient un token d'accès JWT en échange des identifiants.
    Returns:
        Dict contenant :
        - access_token: Le token JWT
        - token_type: Type du token (toujours "bearer")
    """
    try:
        user, access_token = authenticate_user(db, form_data.username, form_data.password)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

#### Endpoints de Données
```python
@router.get("/", response_model=VerreList)
async def read_verres(
    skip: int = 0,
    limit: int = 100,
    fournisseur: Optional[str] = None,
    materiaux: Optional[str] = None,
    indice_min: Optional[float] = None,
    indice_max: Optional[float] = None,
    protection: Optional[bool] = None,
    photochromic: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Liste des verres avec filtres optionnels."""
    filters = VerreFilters(
        fournisseur=fournisseur,
        materiaux=materiaux,
        indice_min=indice_min,
        indice_max=indice_max,
        protection=protection,
        photochromic=photochromic,
    )
    return verres_service.get_verres(db, skip=skip, limit=limit, filters=filters)

@router.get("/{verre_id}", response_model=VerreResponse)
async def read_verre(
    verre_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    """Détails d'un verre par son ID."""
    verre = verres_service.get_verre(db, verre_id)
    if not verre:
        raise HTTPException(status_code=404, detail="Verre non trouvé")
    return verre
```

### 1.2 Règles d'Authentification

#### Système JWT
```python
def create_access_token(data: Dict) -> str:
    """
    Crée un token JWT d'accès.
    Args:
        data: Données à encoder dans le token
    Returns:
        str: Token JWT encodé
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, db: Session) -> dict:
    """Vérifie un token JWT et sa validité en base de données."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if not verify_token_valid(db, token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token révoqué ou expiré",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 1.3 Standards OpenAPI
L'API suit les standards OpenAPI avec :
- Documentation automatique via FastAPI
- Schémas de validation avec Pydantic
- Réponses typées et documentées
- Gestion des erreurs standardisée

## 2. Fonctionnalité de l'API

### 2.1 Accès aux Données
L'API permet :
- La récupération de la liste des verres avec filtres
- L'accès aux détails d'un verre spécifique
- La pagination des résultats
- Le filtrage par différents critères

### 2.2 Sécurité
- Authentification JWT obligatoire
- Validation des tokens
- Protection contre les attaques courantes
- Gestion des erreurs sécurisée

### 2.3 Tests
```python
def test_get_verres(client, auth_headers, test_verre):
    """Test de récupération de la liste des verres."""
    response = client.get("/api/v1/verres/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_get_verres_with_filters(client, auth_headers, test_verre):
    """Test de récupération des verres avec filtres."""
    filters = {
        "fournisseur": "Test Fournisseur",
        "indice_min": 1.0,
        "indice_max": 2.0,
        "protection": True
    }
    response = client.get("/api/v1/verres/", params=filters, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
```

## Conclusion

L'API REST du projet EngraveDetect est fonctionnelle et sécurisée, permettant un accès contrôlé aux données des verres optiques. La documentation technique est complète et suit les standards OpenAPI, tandis que l'authentification JWT assure la sécurité des accès.

### Points Forts
1. API REST complète et documentée
2. Authentification JWT robuste
3. Filtrage et pagination des données
4. Tests automatisés
5. Documentation OpenAPI 