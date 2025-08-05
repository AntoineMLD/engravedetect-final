"""
Module de sécurité pour l'API IA
Gère la validation des entrées, les tokens et les logs de sécurité
"""

import logging
import os
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Optional, Tuple

import jwt
import magic
from fastapi import HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, text

from api_ia.app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    DATABASE_URL,
    SECRET_KEY,
)


# Logger sécurité
def setup_security_logging():
    """
    Configure le logger de sécurité pour l'API.
    """
    # Créer le dossier de logs s'il n'existe pas
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configuration du logger de sécurité
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)

    # Handler pour fichier avec rotation
    file_handler = RotatingFileHandler(f"{log_dir}/security.log", maxBytes=1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.INFO)

    # Format du log
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Ajouter le handler au logger
    security_logger.addHandler(file_handler)

    return security_logger


# Initialiser le logger de sécurité
security_logger = setup_security_logging()

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe en clair contre son hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Génère le hash d'un mot de passe.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token d'accès JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Vérifie et décode un token JWT.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[dict]]:
    """
    Authentifie un utilisateur avec la base de données.
    """
    try:
        # Connexion à la base de données
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            # Requête pour récupérer l'utilisateur
            query = text("SELECT id, username, hashed_password FROM users WHERE username = :username")
            result = connection.execute(query, {"username": username})
            user = result.fetchone()

            if user and verify_password(password, user[2]):  # user[2] = hashed_password
                # Log de connexion réussie
                log_security_event(
                    "login_success",
                    f"Connexion réussie pour l'utilisateur {username}",
                    username,
                )
                return True, {
                    "id": user[0],  # user[0] = id
                    "username": user[1],  # user[1] = username
                }
            else:
                # Log de tentative de connexion échouée
                log_security_event(
                    "login_failed",
                    f"Tentative de connexion échouée pour l'utilisateur {username}",
                    username,
                )
                return False, None

    except Exception as e:
        security_logger.error(f"Erreur lors de l'authentification: {e}")
        return False, None


def validate_image_file(file_content: bytes, filename: Optional[str] = None) -> bool:
    """
    Valide qu'un fichier est bien une image.

    Args:
        file_content: Contenu du fichier en bytes
        filename: Nom du fichier (optionnel)

    Returns:
        True si le fichier est une image valide, False sinon
    """
    try:
        # Vérification du type MIME
        mime_type = magic.from_buffer(file_content, mime=True)
        if not mime_type.startswith("image/"):
            return False

        # Vérification de l'extension (seulement si le nom de fichier est fourni)
        if filename:
            allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
            file_extension = os.path.splitext(filename.lower())[1]
            if file_extension not in allowed_extensions:
                return False

        # Vérification de la taille (max 10MB)
        if len(file_content) > 10 * 1024 * 1024:
            return False

        return True

    except Exception as e:
        security_logger.error(f"Erreur lors de la validation du fichier: {e}")
        return False


def log_security_event(event_type: str, message: str, username: Optional[str] = None):
    """
    Enregistre un événement de sécurité.
    """
    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "message": message,
        "username": username,
        "ip_address": "N/A",  # À implémenter avec FastAPI Request
    }

    if event_type in ["login_failed", "invalid_token", "file_upload_error"]:
        security_logger.warning(message)
    else:
        security_logger.info(message)


# Modèles Pydantic pour la validation
class UserLogin(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


def get_user(username: str) -> Optional[dict]:
    """
    Récupère un utilisateur par son nom d'utilisateur.
    """
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            query = text("SELECT id, username, email FROM users WHERE username = :username")
            result = connection.execute(query, {"username": username})
            user = result.fetchone()

            if user:
                # Utiliser .mappings() pour avoir un dict ou accéder par index
                return {"id": user[0], "username": user[1], "email": user[2]}
            return None

    except Exception as e:
        security_logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
        return None
