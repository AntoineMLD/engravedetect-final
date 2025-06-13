"""
Point d'entrée principal de l'API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .routes import auth, prediction
from .core.openapi_config import setup_openapi
from .core.config import API_TITLE, API_VERSION, API_DESCRIPTION

# Configuration du rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=API_TITLE, description=API_DESCRIPTION, version=API_VERSION)

# Configuration OpenAPI personnalisée
setup_openapi(app)

# Gestionnaire d'erreur pour le rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(prediction.router, prefix="/api/v1", tags=["Prediction"])


@app.get("/", tags=["Health"])
@limiter.limit("10/minute")
async def root():
    """
    Point de terminaison de santé de l'API.
    """
    return {"status": "ok", "message": "API is running"}
