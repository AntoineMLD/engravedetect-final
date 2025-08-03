import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.core.auth.jwt import get_current_user
from src.api.core.auth.models import User as UserModel
from src.api.core.auth.service import authenticate_user
from src.api.core.database.database import get_db
from src.api.core.security import decode_access_token
from src.api.schemas.auth import Token, User, UserCreate
from src.api.services import auth as auth_service

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
    logger = logging.getLogger(__name__)
    logger.info(f"Tentative de confirmation d'email avec token: {token[:10]}...")

    try:
        payload = decode_access_token(token)
        logger.info(f"Token décodé avec succès. Purpose: {payload.get('purpose')}")

        if payload.get("purpose") != "email_confirmation":
            logger.warning(f"Token invalide - mauvais purpose: {payload.get('purpose')}")
            raise HTTPException(status_code=400, detail="Token de confirmation invalide.")

        user_id = int(payload.get("sub"))
        logger.info(f"Recherche de l'utilisateur {user_id}")

        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            logger.warning(f"Utilisateur {user_id} non trouvé")
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

        logger.info(
            f"Token stocké en DB pour user {user_id}: {user.confirmation_token[:10] if user.confirmation_token else 'None'}"
        )
        logger.info(f"Token reçu: {token[:10]}")

        if user.email_confirmed:
            logger.info(f"Email déjà confirmé pour l'utilisateur {user_id}")
            return {"message": "Votre email est déjà confirmé."}

        # Vérifier que le token correspond à celui stocké en base
        if user.confirmation_token != token:
            logger.warning(f"Token ne correspond pas pour l'utilisateur {user_id}")
            logger.warning(f"Token en DB: {user.confirmation_token}")
            logger.warning(f"Token reçu: {token}")
            raise HTTPException(status_code=400, detail="Token de confirmation invalide ou expiré.")

        try:
            user.email_confirmed = True
            user.confirmation_token = None  # Effacer le token après confirmation
            db.add(user)
            logger.info(f"Dirty avant flush pour user {user_id}: {db.dirty}")
            db.flush()
            logger.info(f"Dirty après flush pour user {user_id}: {db.dirty}")
            db.commit()
            db.refresh(user)
            logger.info(f"Email confirmé après commit pour user {user_id}: {user.email_confirmed}")
            return {"message": "Votre email a été confirmé avec succès."}
        except Exception as db_error:
            db.rollback()
            logger.error(f"Erreur DB pour user {user_id}: {db_error}")
            raise HTTPException(status_code=500, detail="Erreur lors de la confirmation de l'email.")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur confirmation email: {e}")
        raise HTTPException(status_code=400, detail="Token invalide ou expiré.")
