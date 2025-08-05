"""
API FastAPI pour la classification des verres
"""

import io
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import (
    Body,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from PIL import Image
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import Response

from api_ia.app.config import API_DESCRIPTION, API_TITLE, API_VERSION
from api_ia.app.database import delete_user_by_username, find_matching_verres, get_verre_details
from api_ia.app.middleware.security import SecurityHeadersMiddleware
from api_ia.app.model_loader import get_embedding, load_model, preprocess_image
from api_ia.app.model_monitoring import model_monitor
from api_ia.app.openapi_config import setup_openapi
from api_ia.app.security import (
    authenticate_user,
    create_access_token,
    get_user,
    log_security_event,
    validate_image_file,
    verify_token,
)
from api_ia.app.similarity_search import get_top_matches, load_references

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
    """
    Schéma Pydantic représentant une correspondance de classe et son score de similarité.

    Attributs :
        class_ (str) : Nom de la classe prédite.
        similarity (float) : Score de similarité cosinus (0 à 1).
    """

    class_: str = None
    similarity: float = 0.0

    class Config:
        populate_by_name = True
        extra = "allow"
        fields = {"class_": "class"}
        schema_extra = {"example": {"class": "e_courbebasse", "similarity": 0.95}}


class MatchResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse du endpoint /match.

    Attributs :
        matches (List[Match]) : Liste des correspondances trouvées.
    """

    matches: List[Match]


class TokenResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse du endpoint /token (authentification).

    Attributs :
        access_token (str) : Token JWT d'accès.
        token_type (str) : Type de token ("bearer").
        version (str) : Version de l'API.
    """

    access_token: str
    token_type: str
    version: str


class EmbeddingResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse du endpoint /embedding.
    """

    embedding: List[float]


class SearchTagsResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse du endpoint /search_tags.
    """

    results: List[dict]


class UserResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse du endpoint /me.
    """

    username: str
    email: str


class DeleteResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse du endpoint /me (DELETE).
    """

    message: str


class RootResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse du endpoint racine.
    """

    message: str


class HealthResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse du endpoint /health.
    """

    status: str


class ModelHealthResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse du endpoint /model/health.
    """

    status: str
    model_metrics: dict
    timestamp: str


# -------------------- Dependencies --------------------


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dépendance FastAPI pour récupérer l'utilisateur courant à partir du token JWT.

    Args:
        token (str): Token JWT d'authentification.

    Returns:
        str: Nom d'utilisateur extrait du token.

    Raises:
        HTTPException: Si le token est invalide ou l'utilisateur non trouvé.
    """
    try:
        token_data = verify_token(token)
        if not token_data or "sub" not in token_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        username = token_data["sub"]
        user = get_user(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return username
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")


# -------------------- Endpoints --------------------


@app.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint d'authentification utilisateur.
    Retourne un token JWT si les identifiants sont valides.

    Args:
        form_data (OAuth2PasswordRequestForm): Formulaire contenant username et password.

    Returns:
        TokenResponse: Token JWT, type et version.

    Raises:
        HTTPException: Si l'authentification échoue.
    """
    success, user = authenticate_user(form_data.username, form_data.password)
    if not success or not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user["username"]})
    log_security_event("TOKEN_CREATED", f"Token for {user['username']}")
    return {"access_token": access_token, "token_type": "bearer", "version": "1"}


@app.post("/embedding", response_model=EmbeddingResponse)
@limiter.limit("5/minute")
async def get_image_embedding(request: Request, file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    """
    Endpoint pour obtenir l'embedding d'une image envoyée.

    Args:
        file (UploadFile): Fichier image à encoder.
        token (str): Token JWT d'authentification.

    Returns:
        dict: Embedding de l'image sous forme de liste.

    Raises:
        HTTPException: Si l'image est invalide ou une erreur survient.
    """
    EMBED_REQUEST_COUNT.inc()
    start_time = time.time()
    try:
        token_data = verify_token(token)
        if not token_data or "sub" not in token_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        image_bytes = await file.read()
        if not validate_image_file(image_bytes, file.filename if file.filename else None):
            raise HTTPException(status_code=400, detail="Invalid image file")
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        embedding = get_embedding(model, img)
        return EmbeddingResponse(embedding=embedding.tolist())
    except Exception as e:
        EMBED_REQUEST_ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"Embedding error: {e}")
    finally:
        EMBED_LATENCY.observe(time.time() - start_time)


@app.post("/match", response_model=MatchResponse)
@limiter.limit("5/minute")
async def get_best_match(request: Request, file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    """
    Endpoint pour obtenir les meilleures correspondances de classes pour une image envoyée.

    Args:
        file (UploadFile): Fichier image à comparer.
        current_user (str): Utilisateur authentifié (dépendance).

    Returns:
        MatchResponse: Liste des classes les plus similaires et leur score.

    Raises:
        HTTPException: Si l'image est invalide ou une erreur survient.
    """
    MATCH_REQUEST_COUNT.inc()
    start_time = time.time()
    success = True

    try:
        image_bytes = await file.read()
        if not validate_image_file(image_bytes, file.filename if file.filename else None):
            raise HTTPException(status_code=400, detail="Invalid image")

        img = Image.open(io.BytesIO(image_bytes)).convert("L")

        # Log pour déboguer l'image reçue
        logger.info(f"Image reçue - Taille: {img.size}, Mode: {img.mode}")

        embedding = get_embedding(model, img)

        # Log pour déboguer l'embedding
        logger.info(
            f"Embedding généré - Shape: {embedding.shape}, Min: {embedding.min():.6f}, Max: {embedding.max():.6f}, Mean: {embedding.mean():.6f}"
        )

        matches = get_top_matches(embedding)
        similarity_scores = [m.get("similarity", 0.0) for m in matches]

        # Monitoring du modèle d'IA
        inference_time = time.time() - start_time

        # Récupérer la classe prédite (première correspondance)
        predicted_class = matches[0].get("class", "") if matches else ""

        model_monitor.update_prediction_metrics(
            embedding=embedding,
            similarity_scores=similarity_scores,
            inference_time=inference_time,
            success=success,
            predicted_class=predicted_class,
            true_class=predicted_class,  # Simulation pour test - en production ce serait la vraie classe
        )

        return {"matches": [{"class_": m.get("class", ""), "similarity": m.get("similarity", 0.0)} for m in matches]}

    except Exception as e:
        success = False
        MATCH_REQUEST_ERRORS.inc()
        logger.error(f"Erreur dans get_best_match: {e}")

        # Monitoring de l'erreur
        if "embedding" in locals():
            inference_time = time.time() - start_time
            model_monitor.update_prediction_metrics(
                embedding=embedding, similarity_scores=[], inference_time=inference_time, success=success
            )

        raise HTTPException(status_code=500, detail=f"Match error: {e}")
    finally:
        MATCH_LATENCY.observe(time.time() - start_time)


@app.post("/search_tags", response_model=SearchTagsResponse)
@limiter.limit("10/minute")
async def search_tags(request: Request, tags: List[str] = Body(...), current_user: str = Depends(get_current_user)):
    """
    Endpoint pour rechercher des verres à partir d'une liste de tags.

    Args:
        tags (List[str]): Liste de tags à rechercher.
        current_user (str): Utilisateur authentifié (dépendance).

    Returns:
        dict: Résultats de la recherche (liste de verres).

    Raises:
        HTTPException: Si la liste de tags est vide ou une erreur survient.
    """
    SEARCH_TAGS_COUNT.inc()
    start_time = time.time()
    try:
        if not tags:
            raise HTTPException(status_code=400, detail="Empty tag list")
        results = find_matching_verres(tags)
        return SearchTagsResponse(results=results)
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
async def get_verre(request: Request, verre_id: int, current_user_email: str = Depends(get_current_user)):
    """
    Endpoint pour obtenir les détails d'un verre par son ID.

    Args:
        verre_id (int): Identifiant du verre à rechercher.
        current_user_email (str): Utilisateur authentifié (dépendance).

    Returns:
        dict: Détails du verre ou message d'erreur.

    Raises:
        HTTPException: Si le verre n'est pas trouvé ou une erreur survient.
    """
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


# -------------------- RGPD Endpoints --------------------

from fastapi.responses import JSONResponse


@app.get("/me", response_model=UserResponse)
async def get_me(current_user: str = Depends(get_current_user)):
    """
    Endpoint RGPD pour obtenir les données personnelles de l'utilisateur authentifié.

    Args:
        current_user (str): Utilisateur authentifié (dépendance).

    Returns:
        dict: Données personnelles (username, email).

    Raises:
        HTTPException: Si l'utilisateur n'est pas trouvé.
    """
    user = get_user(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    # On ne retourne que les infos RGPD pertinentes
    return UserResponse(username=user["username"], email=user["email"])


@app.delete("/me", response_model=DeleteResponse)
async def delete_me(current_user: str = Depends(get_current_user)):
    """
    Endpoint RGPD pour supprimer le compte de l'utilisateur authentifié (droit à l'oubli).

    Args:
        current_user (str): Utilisateur authentifié (dépendance).

    Returns:
        dict: Message de confirmation.

    Raises:
        HTTPException: Si l'utilisateur n'est pas trouvé ou la suppression échoue.
    """
    user = get_user(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    success = delete_user_by_username(current_user)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression du compte")
    log_security_event("USER_DELETED", f"Suppression du compte pour {current_user}")
    return DeleteResponse(message="Compte supprimé avec succès")


@app.get("/", response_model=RootResponse)
async def root():
    """
    Endpoint racine de l'API.

    Returns:
        dict: Message de bienvenue.
    """
    return RootResponse(message="Bienvenue sur l'API de classification d'images")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint de vérification de santé de l'API.

    Returns:
        dict: Statut de santé.
    """
    return HealthResponse(status="healthy")


@app.get("/model/health", response_model=ModelHealthResponse)
async def model_health_check():
    """
    Endpoint de vérification de santé du modèle d'IA.

    Returns:
        dict: Métriques de santé du modèle d'IA.
    """
    try:
        model_status = model_monitor.get_model_health_status()
        return ModelHealthResponse(status="healthy", model_metrics=model_status, timestamp=datetime.now().isoformat())
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut du modèle: {e}")
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}


@app.get("/metrics")
def metrics():
    """
    Endpoint Prometheus pour exporter les métriques de monitoring.

    Returns:
        Response: Données Prometheus formatées.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
