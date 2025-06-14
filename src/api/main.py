from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.v1 import auth, verres
from src.api.core.config import settings

# Création de l'application FastAPI
app = FastAPI(
    title="API Verres Optiques",
    version=settings.APP_VERSION,
    description=settings.API_DESCRIPTION,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines exactes
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
