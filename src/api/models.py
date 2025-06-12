from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class VerreBase(BaseModel):
    nom: str
    variante: Optional[str] = None
    hauteur_min: Optional[int] = None
    hauteur_max: Optional[int] = None
    indice: Optional[float] = None
    protection: Optional[bool] = None
    photochromic: Optional[bool] = None


class VerreResponse(VerreBase):
    id: int
    fournisseur: Optional[str] = None
    materiau: Optional[str] = None
    gamme: Optional[str] = None
    serie: Optional[str] = None

    class Config:
        from_attributes = True
