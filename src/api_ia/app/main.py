"""
API FastAPI pour la classification des verres
"""

import logging
import io
import time
from pathlib import Path
from typing import List
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Request, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from api_ia.app.model_loader import load_model, preprocess_image, get_embedding
from api_ia.app.similarity_search import get_top_matches, load_references
from api_ia.app.database import find_matching_verres, get_verre_details
from api_ia.app.security import (
    authenticate_user,
    create_access_token,
    get_user,
    verify_token,
    validate_image_file,
    log_security_event,
)
from api_ia.app.middleware.security import SecurityHeadersMiddleware
from api_ia.app.config import ADMIN_EMAIL, ADMIN_PASSWORD, API_TITLE, API_VERSION, API_DESCRIPTION
from api_ia.app.openapi_config import setup_openapi
from pydantic import BaseModel

# Load env variables
load_dotenv()

# Logging config
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=True)

# -------------------- Prometheus metrics --------------------

# /match
MATCH_REQUEST_COUNT = Counter("match_requests_total", "Total /match requests")
MATCH_REQUEST_ERRORS = Counter("match_request_errors_total", "Errors in /match requests")
MATCH_LATENCY = Histogram("match_latency_seconds", "Latency for /match")

# /embedding
EMBED_REQUEST_COUNT = Counter("embedding_requests_total", "Total /embedding requests")
EMBED_REQUEST_ERRORS = Counter("embedding_request_errors_total", "Errors in /embedding requests")
EMBED_LATENCY = Histogram("embedding_latency_seconds", "Latency for /embedding")

# /search_tags
SEARCH_TAGS_COUNT = Counter("search_tags_requests_total", "Total /search_tags requests")
SEARCH_TAGS_ERRORS = Counter("search_tags_errors_total", "Errors in /search_tags")
SEARCH_TAGS_LATENCY = Histogram("search_tags_latency_seconds", "Latency for /search_tags")

# /verre/{id}
VERRE_DETAIL_COUNT = Counter("verre_details_requests_total", "Total /verre/{id} requests")
VERRE_DETAIL_ERRORS = Counter("verre_details_errors_total", "Errors in /verre/{id}")
VERRE_DETAIL_LATENCY = Histogram("verre_details_latency_seconds", "Latency for /verre/{id}")

# -------------------- FastAPI Setup --------------------

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_openapi(app)

# -------------------- Model Load --------------------

try:
    logger.info("Loading model...")
    model = load_model()
    load_references(model)
    logger.info("Model and references loaded")
except Exception as e:
    logger.error(f"Error loading model or references: {e}")
    raise

# -------------------- Pydantic Schemas --------------------


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
    version: str


# -------------------- Dependencies --------------------


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        token_data = verify_token(token)
        user = get_user(token_data.username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return token_data.username
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")


# -------------------- Endpoints --------------------


@app.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token, version = create_access_token(user["username"])
    log_security_event("TOKEN_CREATED", f"Token v{version} for {user['username']}")
    return {"access_token": access_token, "token_type": "bearer", "version": str(version)}


@app.post("/embedding")
@limiter.limit("5/minute")
async def get_image_embedding(request: Request, file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    EMBED_REQUEST_COUNT.inc()
    start_time = time.time()
    try:
        verify_token(token)
        image_bytes = await file.read()
        if not validate_image_file(image_bytes):
            raise HTTPException(status_code=400, detail="Invalid image file")
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        embedding = get_embedding(model, img)
        return {"embedding": embedding.tolist()}
    except Exception as e:
        EMBED_REQUEST_ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"Embedding error: {e}")
    finally:
        EMBED_LATENCY.observe(time.time() - start_time)


@app.post("/match", response_model=MatchResponse)
@limiter.limit("5/minute")
async def get_best_match(request: Request, file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    MATCH_REQUEST_COUNT.inc()
    start_time = time.time()
    try:
        image_bytes = await file.read()
        if not validate_image_file(image_bytes):
            raise HTTPException(status_code=400, detail="Invalid image")
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        embedding = get_embedding(model, img)
        matches = get_top_matches(embedding)
        return {"matches": [{"class_": m.get("class", ""), "similarity": m.get("similarity", 0.0)} for m in matches]}
    except Exception as e:
        MATCH_REQUEST_ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"Match error: {e}")
    finally:
        MATCH_LATENCY.observe(time.time() - start_time)


@app.post("/search_tags")
@limiter.limit("10/minute")
async def search_tags(request: Request, tags: List[str] = Body(...), current_user: str = Depends(get_current_user)):
    SEARCH_TAGS_COUNT.inc()
    start_time = time.time()
    try:
        if not tags:
            raise HTTPException(status_code=400, detail="Empty tag list")
        results = find_matching_verres(tags)
        return {"results": results}
    except Exception as e:
        SEARCH_TAGS_ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"search_tags error: {e}")
    finally:
        SEARCH_TAGS_LATENCY.observe(time.time() - start_time)


@app.get(
    "/verre/{verre_id}",
    summary="Obtenir les détails d'un verre",
    description="Récupère les détails complets d'un verre par son ID",
)
@limiter.limit("20/minute")
async def get_verre(
    request: Request, verre_id: int, current_user_email: str = Depends(get_current_user)  # ✅ Ajouté pour SlowAPI
):
    VERRE_DETAIL_COUNT.inc()  # Incrémenter le compteur de requêtes
    start_time = time.time()  # Démarrer le chronomètre

    try:
        logger.info(f"Recherche du verre avec ID: {verre_id}")
        verre = get_verre_details(verre_id)

        if not verre:
            logger.warning(f"Verre avec ID {verre_id} non trouvé")
            return {"error": "Verre non trouvé"}

        logger.info(f"Verre trouvé: {verre['nom']}")
        return {"verre": verre}

    except Exception as e:
        VERRE_DETAIL_ERRORS.inc()  # Incrémenter le compteur d'erreurs
        logger.error(f"Erreur lors de la récupération du verre: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du verre: {str(e)}")

    finally:
        VERRE_DETAIL_LATENCY.observe(time.time() - start_time)  # Enregistrer la latence


@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API de classification d'images"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
