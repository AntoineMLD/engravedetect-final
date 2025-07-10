# src/api/core/auth/jwt.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from ..config import settings
from ..database.session import get_db
from .token_service import verify_token_valid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def verify_token(token: str, db: Session) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if not verify_token_valid(db, token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token révoqué ou expiré", headers={"WWW-Authenticate": "Bearer"})
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide", headers={"WWW-Authenticate": "Bearer"})

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    return verify_token(token, db)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
