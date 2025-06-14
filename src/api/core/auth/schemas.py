from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs."""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur."""
    password: str


class UserResponse(UserBase):
    """Schéma pour la réponse d'un utilisateur."""
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schéma pour les tokens."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schéma pour les données du token."""
    username: str | None = None 