from sqlalchemy.orm import Session
from ..core.auth.models import User as UserModel
from ..core.auth.service import create_user as create_user_service


def create_user(db: Session, user_data: dict):
    """Crée un nouvel utilisateur."""
    return create_user_service(db, user_data)


def get_user(db: Session, user_id: int):
    """Récupère un utilisateur par son ID."""
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """Récupère un utilisateur par son email."""
    return db.query(UserModel).filter(UserModel.email == email).first()


def revoke_token(db: Session, token: str):
    """Révoque un token JWT."""
    # La révocation est gérée dans le service d'authentification
    pass
