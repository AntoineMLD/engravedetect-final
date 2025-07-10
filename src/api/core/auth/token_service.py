from datetime import datetime, timedelta
from fastapi import Request
from sqlalchemy.orm import Session
from .models import Token
from ..config import settings

def create_db_token(db: Session, user_id: int, token: str, request: Request = None) -> Token:
    """Crée un nouveau token en base de données."""
    expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    device_info = None
    if request:
        user_agent = request.headers.get("user-agent")
        device_info = user_agent[:200] if user_agent else None

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
