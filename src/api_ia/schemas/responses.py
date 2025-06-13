"""
Schémas Pydantic pour les réponses API.
"""

from pydantic import BaseModel
from typing import List


class Match(BaseModel):
    class_: str = None
    similarity: float = 0.0

    class Config:
        populate_by_name = True
        extra = "allow"
        fields = {"class_": "class"}
        schema_extra = {"example": {"class": "e_courbebasse", "similarity": 0.95}}


class MatchResponse(BaseModel):
    matches: List[Match]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ValidationResponse(BaseModel):
    status: str
    message: str
