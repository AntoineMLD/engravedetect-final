from datetime import datetime, timedelta
from fastapi import Request
from sqlalchemy.orm import Session
from src.api.core.auth.models import Token
from src.api.core.config import settings  # import absolu

def create_db_token(db: Session, user_id: int, token: str, request: Request = None) -> Token:
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

def verify_token_valid(db: Session, token: str) -> bool:
    db_token = db.query(Token).filter(Token.token == token, Token.is_active == True).first()
    return db_token is not None
