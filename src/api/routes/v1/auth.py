from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict
from src.api.core.database.database import get_db
from src.api.core.security import decode_access_token
from src.api.core.auth.jwt import get_current_user
from src.api.schemas.auth import UserCreate, User, Token
from src.api.services import auth as auth_service
from src.api.core.auth.service import authenticate_user
from src.api.core.auth.models import User as UserModel

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur.
    """
    return auth_service.create_user(db, user)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Obtient un token d'accès JWT en échange des identifiants.
    """
    try:
        user, access_token = authenticate_user(db, form_data.username, form_data.password)
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    """
    Déconnexion utilisateur.
    """
    auth_service.revoke_token(db, token)
    return {"message": "Déconnexion réussie"}

@router.get("/me", response_model=dict)
async def read_users_me(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Retourne les informations de l'utilisateur connecté.
    """
    return current_user

@router.get("/confirm")
def confirm_email(token: str, db: Session = Depends(get_db)):
    """Confirme l'adresse email d'un utilisateur."""
    try:
        payload = decode_access_token(token)
        if payload.get("purpose") != "email_confirmation":
            raise HTTPException(status_code=400, detail="Token de confirmation invalide.")

        user_id = int(payload.get("sub"))
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

        if user.email_confirmed:
            return {"message": "Votre email est déjà confirmé."}

        try:
            user.email_confirmed = True
            db.add(user)              
            print("Dirty avant flush:", db.dirty)
            db.flush()                 
            print("Dirty après flush:", db.dirty)
            db.commit()
            db.refresh(user)
            print("Email confirmé après commit:", user.email_confirmed)
            return {"message": "Votre email a été confirmé avec succès."}
        except Exception as db_error:
            db.rollback()
            print(f"[ERROR DB] {db_error}")
            raise HTTPException(status_code=500, detail="Erreur lors de la confirmation de l'email.")

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR confirm_email] {e}")
        raise HTTPException(status_code=400, detail="Token invalide ou expiré.")
