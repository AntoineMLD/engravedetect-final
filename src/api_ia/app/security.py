"""
Module de sécurité pour l'API
Gère la validation des entrées, les tokens et les logs de sécurité
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from pydantic import BaseModel, EmailStr
import jwt
from fastapi import HTTPException, status
import logging
import os
from logging.handlers import RotatingFileHandler
from passlib.context import CryptContext
from api_ia.app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, ROTATION_THRESHOLD_MINUTES, LOG_DIR
from .database import get_db_connection
import magic


# Logger sécurité
def setup_security_logging():
    log_path = os.path.join(LOG_DIR, "security")
    os.makedirs(log_path, exist_ok=True)

    logger = logging.getLogger("security")
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(os.path.join(log_path, "security.log"), maxBytes=1024 * 1024, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


security_logger = setup_security_logging()


# Modèles
class TokenData(BaseModel):
    username: str
    exp: datetime
    token_version: Optional[int] = 0


class UserCredentials(BaseModel):
    email: EmailStr
    password: str


# Configs
TOKEN_SETTINGS = {
    "SECRET_KEY": SECRET_KEY,
    "ALGORITHM": ALGORITHM,
    "ACCESS_TOKEN_EXPIRE_MINUTES": ACCESS_TOKEN_EXPIRE_MINUTES,
    "ROTATION_THRESHOLD_MINUTES": ROTATION_THRESHOLD_MINUTES,
}

# Token versions (en mémoire)
token_versions = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


# Auth
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_user(username: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, hashed_password, is_active FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "email": row[2], "hashed_password": row[3], "is_active": row[4]}
    except Exception as e:
        security_logger.error(f"Erreur lors de la récupération de l'utilisateur : {e}")
    return None


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


# Tokens
def create_access_token(username: str) -> Tuple[str, int]:
    current_version = token_versions.get(username, 0) + 1
    token_versions[username] = current_version

    expire = datetime.utcnow() + timedelta(minutes=TOKEN_SETTINGS["ACCESS_TOKEN_EXPIRE_MINUTES"])
    payload = {"sub": username, "exp": expire, "token_version": current_version}

    token = jwt.encode(payload, TOKEN_SETTINGS["SECRET_KEY"], algorithm=TOKEN_SETTINGS["ALGORITHM"])

    log_security_event("TOKEN_CREATED", f"Token v{current_version} généré pour {username}")
    return token, current_version


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, TOKEN_SETTINGS["SECRET_KEY"], algorithms=[TOKEN_SETTINGS["ALGORITHM"]])
        username = payload.get("sub")
        token_version = payload.get("token_version", 0)

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token (missing subject)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        stored_version = token_versions.get(username, 0)
        if token_version == stored_version:  # On accepte uniquement la version exacte
            return TokenData(username=username, exp=datetime.fromtimestamp(payload["exp"]), token_version=token_version)
        else:
            log_security_event("TOKEN_INVALID_VERSION", f"Ancienne version de token pour {username}", "WARNING")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token obsolète", 
                headers={"WWW-Authenticate": "Bearer"}
            )

    except jwt.ExpiredSignatureError:
        log_security_event("TOKEN_EXPIRED", "Token expiré", "WARNING")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token expiré", 
            headers={"WWW-Authenticate": "Bearer"}
        )

    except jwt.PyJWTError as e:
        log_security_event("TOKEN_INVALID", f"Erreur JWT : {str(e)}", "ERROR")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token invalide", 
            headers={"WWW-Authenticate": "Bearer"}
        )


# Validation fichier
def check_mime_type(file_content: bytes) -> Tuple[bool, str]:
    """
    Vérifie le type MIME d'un fichier en utilisant python-magic.
    
    Args:
        file_content (bytes): Contenu du fichier à vérifier
        
    Returns:
        Tuple[bool, str]: (est_valide, type_mime)
    """
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file_content)
        
        # Types MIME autorisés pour les images
        allowed_mime_types = {
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/webp'
        }
        
        return mime_type in allowed_mime_types, mime_type
    except Exception as e:
        log_security_event("MIME_CHECK_ERROR", str(e), "ERROR")
        return False, "unknown"


def validate_image_file(file_content: bytes, max_size: int = 5 * 1024 * 1024) -> bool:
    """
    Valide un fichier image en vérifiant sa taille et son type MIME.
    
    Args:
        file_content (bytes): Contenu du fichier à valider
        max_size (int): Taille maximale autorisée en octets (défaut: 5MB)
        
    Returns:
        bool: True si le fichier est valide, False sinon
    """
    # Vérification de la taille
    if len(file_content) > max_size:
        log_security_event("FILE_TOO_LARGE", f"Taille : {len(file_content)} > {max_size}", "WARNING")
        return False

    # Vérification du type MIME
    is_valid_mime, mime_type = check_mime_type(file_content)
    if not is_valid_mime:
        log_security_event("INVALID_FILE_TYPE", f"Type MIME non autorisé : {mime_type}", "WARNING")
        return False

    # Vérification des signatures de fichier (double vérification)
    allowed_signatures = [b"\xFF\xD8\xFF", b"\x89\x50\x4E\x47"]
    is_valid_signature = any(file_content.startswith(sig) for sig in allowed_signatures)

    if not is_valid_signature:
        log_security_event("INVALID_FILE_SIGNATURE", "Signature de fichier non autorisée", "WARNING")
        return False

    return True


# Logs sécurité
def log_security_event(event_type: str, details: str, level: str = "INFO"):
    message = f"{event_type} - {details}"
    if level == "ERROR":
        security_logger.error(message)
    elif level == "WARNING":
        security_logger.warning(message)
    else:
        security_logger.info(message)
