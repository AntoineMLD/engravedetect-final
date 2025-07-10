from datetime import datetime
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from .models import User
from ...core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_confirmation_token
)
from .token_service import create_db_token

def authenticate_user(db: Session, username: str, password: str, request: Request = None) -> tuple[User, str]:
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Veuillez confirmer votre adresse email avant de vous connecter."
        )

    user.last_login = datetime.utcnow()
    access_token = create_access_token({"sub": user.username})
    create_db_token(db, user.id, access_token, request)
    db.commit()

    return user, access_token
