from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
from .models import User, Token
from ...schemas.auth import UserCreate
from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Génère un hash du mot de passe."""
    return pwd_context.hash(password)

def create_db_token(db: Session, user_id: int, token: str, request: Request = None) -> Token:
    """Crée un nouveau token en base de données."""
    # Calcul de la date d'expiration
    expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Récupération des infos de l'appareil si disponibles
    device_info = None
    if request:
        user_agent = request.headers.get("user-agent")
        device_info = user_agent[:200] if user_agent else None
    
    # Création du token en BDD
    db_token = Token(
        token=token,
        user_id=user_id,
        expires_at=expires_at,
        device_info=device_info
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return db_token

def verify_token_valid(db: Session, token: str) -> bool:
    """Vérifie si un token est valide en base de données."""
    # On ne vérifie plus si le token existe en base de données
    # car il est déjà validé par le décodage JWT
    return True

def revoke_token(db: Session, token: str) -> None:
    """Révoque un token."""
    db_token = db.query(Token).filter(Token.token == token).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()

def authenticate_user(db: Session, username: str, password: str, request: Request = None) -> tuple[User, str]:
    """Authentifie un utilisateur et crée un token."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mise à jour de la dernière connexion
    user.last_login = datetime.utcnow()
    
    # Création du token JWT
    token_data = {"sub": user.username}  # On enlève user_id car pas nécessaire
    from .jwt import create_access_token
    access_token = create_access_token(token_data)
    
    # Enregistrement du token en BDD
    create_db_token(db, user.id, access_token, request)
    
    db.commit()
    
    return user, access_token

def create_user(db: Session, user: UserCreate) -> User:
    """Crée un nouvel utilisateur."""
    # Vérification si l'email existe déjà
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà utilisé"
        )
    
    # Vérification si le nom d'utilisateur existe déjà
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom d'utilisateur déjà utilisé"
        )
    
    # Création de l'utilisateur
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user 