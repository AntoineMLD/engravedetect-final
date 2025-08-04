"""
API principale pour EngraveDetect

Ce module contient l'application FastAPI principale pour la gestion
des verres optiques et l'authentification des utilisateurs.

Fonctionnalités :
- Configuration de l'API FastAPI
- Gestion des routes d'authentification et de verres
- Configuration CORS et middleware
- Logging et monitoring

Auteur : Équipe de développement
Version : 1.0.0
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.core.config import settings
from src.api.routes.v1 import auth, verres

# Configuration détaillée du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Loggers spécifiques
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logging.getLogger("src.api").setLevel(logging.INFO)
logging.getLogger("fastapi").setLevel(logging.INFO)

# Création de l'application FastAPI
app = FastAPI(
    title="API Verres Optiques",
    version=settings.APP_VERSION,
    description=settings.API_DESCRIPTION,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes v1
app.include_router(verres.router, prefix="/api/v1/verres", tags=["verres"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/")
def root():
    """Route racine de l'API."""
    return {"message": "Bienvenue sur l'API de gestion des verres optiques"}


# Point de terminaison de santé
@app.get("/api/v1/health")
def health_check():
    """Vérifie que l'API est en fonctionnement."""
    return {"status": "healthy"}
