"""
Schémas Pydantic pour les requêtes API.
"""

from pydantic import BaseModel


class PredictionValidation(BaseModel):
    predicted_class: str


class UserCredentials(BaseModel):
    email: str
    password: str
