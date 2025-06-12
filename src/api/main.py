from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routes.v1 import auth, verres
from .core.database.init_db import init_db

# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.API_DESCRIPTION
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation de la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    init_db()

# Routes v1
app.include_router(
    verres.router,
    prefix=settings.API_V1_STR + "/verres",
    tags=["verres"]
)

app.include_router(
    auth.router,
    prefix=settings.API_V1_STR + "/auth",
    tags=["auth"]
)

@app.get("/", tags=["status"])
async def root():
    """Point d'entrée de l'API."""
    return {
        "status": "ok",
        "version": settings.APP_VERSION
    }

# Point de terminaison de santé
@app.get("/health")
def health_check():
    """Vérifie que l'API est en fonctionnement."""
    return {"status": "ok"} 