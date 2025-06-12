from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict

from ...core.database.session import get_db
from ...core.auth import service
from ...core.auth.jwt import get_current_user, create_access_token
from ...schemas.auth import UserCreate, User, Token

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur.
    
    - **email**: Email unique de l'utilisateur
    - **username**: Nom d'utilisateur unique
    - **password**: Mot de passe (sera haché)
    """
    return service.create_user(db, user)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, str]:
    """
    Obtient un token d'accès JWT en échange des identifiants.

    Cette route permet d'obtenir un token JWT qui sera nécessaire pour accéder
    aux autres endpoints de l'API. Le token a une durée de validité limitée
    définie dans la configuration.

    Args:
        form_data: Formulaire contenant username et password

    Returns:
        Dict contenant :
        - access_token: Le token JWT
        - token_type: Type du token (toujours "bearer")

    Raises:
        HTTPException 401: Si les identifiants sont invalides
    """
    # Ici, vous devriez vérifier les identifiants dans votre base de données
    # Pour l'exemple, on accepte tout utilisateur avec un mot de passe
    if not form_data.password:
        raise HTTPException(
            status_code=401,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(
    db: Session = Depends(get_db),
    token: str = Depends(get_current_user)
):
    """
    Déconnexion utilisateur.
    Révoque le token actuel.
    """
    service.revoke_token(db, token)
    return {"message": "Déconnexion réussie"}

@router.get("/me", response_model=dict)
async def read_users_me(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Retourne les informations de l'utilisateur connecté.

    Cette route permet de vérifier que le token JWT est valide et de récupérer
    les informations de l'utilisateur associé.

    Returns:
        Dict contenant les informations de l'utilisateur :
        - sub: L'identifiant de l'utilisateur (email)

    Raises:
        HTTPException 401: Si le token est invalide ou expiré
    """
    return current_user 