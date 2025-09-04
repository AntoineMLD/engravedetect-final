"""
API FastAPI pour la classification des verres EngraveDetect.
Sécurité, monitoring Prometheus, endpoints IA.
"""

import io
import logging
import time
from datetime import datetime
from typing import List, Optional

import numpy as np
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from PIL import Image
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import Response

# Modules internes
from api_ia.app.config import API_DESCRIPTION, API_TITLE, API_VERSION
from api_ia.app.database import delete_user_by_username, find_matching_verres, get_verre_details
from api_ia.app.middleware.security import SecurityHeadersMiddleware
from api_ia.app.model_loader import get_embedding, load_model
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

# -------------------- Initialisation --------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("engravedetect.api_ia")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=True)
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

# -------------------- Chargement du modèle --------------------
try:
    logger.info("Chargement du modèle...")
    model = load_model()
    load_references(model)
    logger.info("Modèle et références chargés")
    # Initialise le drift pour éviter "No data" au démarrage
    model_monitor.update_drift(0.0)
except Exception as e:
    logger.error(f"Erreur au chargement du modèle: {e}")
    raise

# -------------------- Schemas Pydantic --------------------
class Match(BaseModel):
    class_: str
    similarity: float

    class Config:
        fields = {"class_": "class"}

class MatchResponse(BaseModel):
    matches: List[Match]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    version: str

class EmbeddingResponse(BaseModel):
    embedding: List[float]

class SearchTagsResponse(BaseModel):
    results: List[dict]

class UserResponse(BaseModel):
    username: str
    email: str

class DeleteResponse(BaseModel):
    message: str

class RootResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str

class ModelHealthResponse(BaseModel):
    status: str
    model_metrics: dict
    timestamp: str

# -------------------- Dépendances --------------------
async def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)
    if not token_data or "sub" not in token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = token_data["sub"]
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return username

# -------------------- Endpoints --------------------
@app.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    success, user = authenticate_user(form_data.username, form_data.password)
    if not success or not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user["username"]})
    log_security_event("TOKEN_CREATED", f"Token for {user['username']}")
    return {"access_token": access_token, "token_type": "bearer", "version": API_VERSION}

@app.post("/embedding", response_model=EmbeddingResponse)
@limiter.limit("5/minute")
async def get_image_embedding(
    request: Request,
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
):
    start = time.time()
    try:
        token_data = verify_token(token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid token")

        image_bytes = await file.read()
        if not validate_image_file(image_bytes, file.filename if file.filename else None):
            raise HTTPException(status_code=400, detail="Invalid image file")

        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        embedding = get_embedding(model, img)

        # Monitoring (pas de classes ici)
        model_monitor.observe_prediction(
            embedding=embedding,
            similarity_scores=[],
            inference_time=time.time() - start,
            success=True,
            predicted_class="",
            true_class=None,
            image_info={
                "brightness": float(np.mean(np.array(img)) / 255.0),
                "width": img.width,
                "height": img.height,
                "payload_size": len(image_bytes),
            },
        )

        return EmbeddingResponse(embedding=embedding.tolist())

    except Exception as e:
        model_monitor.observe_prediction(
            embedding=None,
            similarity_scores=[],
            inference_time=time.time() - start,
            success=False,
            predicted_class="",
            true_class=None,
            image_info=None,
        )
        raise HTTPException(status_code=500, detail=f"Embedding error: {e}")

@app.post("/match", response_model=MatchResponse)
@limiter.limit("5/minute")
async def get_best_match(
    request: Request,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    x_true_class: Optional[str] = Header(default=None, convert_underscores=False),
):
    start = time.time()
    try:
        image_bytes = await file.read()
        if not validate_image_file(image_bytes, file.filename if file.filename else None):
            raise HTTPException(status_code=400, detail="Invalid image")

        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        embedding = get_embedding(model, img)

        matches = get_top_matches(embedding, k=5)
        similarity_scores = [float(m["similarity"]) for m in matches]
        predicted_class = matches[0]["class"] if matches else ""

        # Monitoring
        model_monitor.observe_prediction(
            embedding=embedding,
            similarity_scores=similarity_scores,
            inference_time=time.time() - start,
            success=True,
            predicted_class=predicted_class,
            true_class=x_true_class,
            image_info={
                "brightness": float(np.mean(np.array(img)) / 255.0),
                "width": img.width,
                "height": img.height,
                "payload_size": len(image_bytes),
            },
        )

        # Panneaux “dernière classe” & “tag attendu”
        if predicted_class:
            model_monitor.set_last_predicted_class(predicted_class)
        if x_true_class:
            model_monitor.set_last_expected_tag(x_true_class)

        return {"matches": [{"class_": m["class"], "similarity": m["similarity"]} for m in matches]}

    except Exception as e:
        model_monitor.observe_prediction(
            embedding=None,
            similarity_scores=[],
            inference_time=time.time() - start,
            success=False,
            predicted_class="",
            true_class=None,
            image_info=None,
        )
        raise HTTPException(status_code=500, detail=f"Match error: {e}")

@app.post("/search_tags", response_model=SearchTagsResponse)
async def search_tags(tags: List[str] = Body(...), current_user: str = Depends(get_current_user)):
    # Enregistre le tag "attendu" (on prend le premier comme intention utilisateur)
    if tags:
        model_monitor.set_last_expected_tag(tags[0])

    results = find_matching_verres(tags)
    return SearchTagsResponse(results=results)

@app.get("/verre/{verre_id}")
async def get_verre(verre_id: int, current_user_email: str = Depends(get_current_user)):
    verre = get_verre_details(verre_id)
    if not verre:
        raise HTTPException(status_code=404, detail="Verre non trouvé")
    return {"verre": verre}

@app.get("/me", response_model=UserResponse)
async def get_me(current_user: str = Depends(get_current_user)):
    user = get_user(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return UserResponse(username=user["username"], email=user["email"])

@app.delete("/me", response_model=DeleteResponse)
async def delete_me(current_user: str = Depends(get_current_user)):
    success = delete_user_by_username(current_user)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression du compte")
    log_security_event("USER_DELETED", f"Suppression du compte {current_user}")
    return DeleteResponse(message="Compte supprimé avec succès")

@app.get("/", response_model=RootResponse)
async def root():
    return RootResponse(message="Bienvenue sur l'API de classification d'images")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")

@app.get("/model/health", response_model=ModelHealthResponse)
async def model_health_check():
    return ModelHealthResponse(
        status="healthy",
        model_metrics=model_monitor.get_model_health_status(),
        timestamp=datetime.now().isoformat(),
    )

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
