from sqlalchemy.orm import Session
from ..schemas.auth import UserCreate, User

def get_user_by_email(db: Session, email: str):
    """Récupère un utilisateur par son email."""
    return None

def create_user(db: Session, user: UserCreate):
    """Crée un nouvel utilisateur."""
    return None

def revoke_token(db: Session, token: str):
    """Révoque un token."""
    pass 