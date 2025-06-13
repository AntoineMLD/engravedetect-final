"""
Security module for authentication and authorization.
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Tuple
from fastapi import HTTPException, status
from pydantic import BaseModel

# Configuration de la sécurité
SECRET_KEY = "your-secret-key"  # À remplacer par une vraie clé secrète en production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    email: str
    version: int
    exp: datetime


def create_access_token(email: str) -> Tuple[str, int]:
    """
    Crée un token JWT avec une version incrémentée.
    """
    version = 1  # Dans une vraie application, on stockerait et incrémenterait cette version
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = TokenData(email=email, version=version, exp=expire)

    encoded_jwt = jwt.encode(to_encode.dict(), SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt, version


def verify_token(token: str) -> Tuple[TokenData, bool]:
    """
    Vérifie un token JWT et indique s'il doit être renouvelé.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)

        # Vérifier si le token est expiré
        if datetime.utcnow() > token_data.exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expiré",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Vérifier si le token doit être renouvelé (par exemple, si plus de 50% du temps est écoulé)
        time_elapsed = datetime.utcnow() - (token_data.exp - timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        should_rotate = time_elapsed > timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES / 2)

        return token_data, should_rotate

    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_image_file(file_bytes: bytes) -> bool:
    """
    Valide un fichier image.
    """
    # Implement actual image validation here
    return True


def log_security_event(event_type: str, description: str, level: str = "INFO"):
    """
    Log un événement de sécurité.
    """
    log_message = f"Security event: {event_type} - {description}"
    if level == "WARNING":
        logger.warning(log_message)
    elif level == "ERROR":
        logger.error(log_message)
    else:
        logger.info(log_message)
