from datetime import datetime
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from .models import User, Token
from .utils import verify_password, get_password_hash, create_db_token

def authenticate_user(db: Session, username: str, password: str, request: Request = None) -> tuple[User, str]:
    """
    Authentifie un utilisateur et crée un token s'il a confirmé son email.
    """
    from .jwt import create_access_token

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Vérification de la confirmation de l'email
    if not user.email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Veuillez confirmer votre adresse email avant de vous connecter."
        )

    # ✅ Mettre à jour la date de dernière connexion
    user.last_login = datetime.utcnow()

    # ✅ Génération du JWT
    token_data = {"sub": user.username}
    access_token = create_access_token(token_data)

    # ✅ Enregistrer le token en BDD
    create_db_token(db, user.id, access_token, request)

    db.commit()

    return user, access_token
