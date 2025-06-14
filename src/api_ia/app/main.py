"""
API FastAPI pour la classification des verres
"""

import logging
import sys
import os
from pathlib import Path

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, UploadFile, File, Request, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from api_ia.app.model_loader import load_model, preprocess_image, get_embedding
from api_ia.app.similarity_search import get_top_matches, load_references, reference_embeddings
from api_ia.app.database import find_matching_verres, get_verre_details, get_verre_staging_details, get_db_connection
from api_ia.app.security import (
    UserCredentials,
    create_access_token,
    verify_token,
    validate_image_file,
    log_security_event,
    authenticate_user,
    get_user
)
from api_ia.app.monitoring.metrics_collector import monitor
from api_ia.app.config import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION
)
from api_ia.app.openapi_config import setup_openapi
import io 
from PIL import Image
from datetime import datetime
import time
import numpy as np
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modèles de données
class PredictionValidation(BaseModel):
    predicted_class: str

# Utilisation d'une classe de modèle plus simple pour éviter les problèmes de validation
class Match(BaseModel):
    class_: str = None
    similarity: float = 0.0
    
    class Config:
        populate_by_name = True
        extra = "allow"  # Accepter des champs supplémentaires
        fields = {
            'class_': 'class'
        }
        schema_extra = {
            "example": {
                "class": "e_courbebasse",
                "similarity": 0.95
            }
        }

class MatchResponse(BaseModel):
    matches: List[Match]
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ValidationResponse(BaseModel):
    status: str
    message: str

# Initialisation du limiteur de taux
limiter = Limiter(key_func=get_remote_address)

# Création de l'application FastAPI
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration du schéma OpenAPI personnalisé
setup_openapi(app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialisation du modèle et des références
try:
    logger.info("Chargement du modèle...")
    model = load_model()
    logger.info("Modèle chargé avec succès")
    
    logger.info("Chargement des références...")
    load_references(model)
    logger.info("Références chargées avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement du modèle ou des références: {e}")
    raise

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dépendance pour obtenir l'utilisateur actuel à partir du token
    """
    token_data = verify_token(token)
    user = get_user(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/token", response_model=TokenResponse, summary="Obtenir un token d'authentification", description="Authentifie l'utilisateur et renvoie un token JWT")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Point de terminaison pour l'authentification
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, _ = create_access_token(user["username"])
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/embedding", summary="Obtenir l'embedding d'une image", description="Calcule et renvoie l'embedding vectoriel d'une image")
@limiter.limit("5/minute")
async def get_image_embedding(request: Request, file: UploadFile = File(...), token: str = Depends(verify_token)):
    """
    Calcule l'embedding d'une image
    """
    image_bytes = await file.read()
    if not validate_image_file(image_bytes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )
        
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    embedding = get_embedding(model, img)
    return {"embedding": embedding.tolist()}

@app.post("/match", response_model=MatchResponse, summary="Trouver les correspondances pour une image", description="Analyse une image et renvoie les classes les plus similaires")
@limiter.limit("5/minute")
async def get_best_match(
    request: Request,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """
    Point de terminaison pour la classification d'image
    """
    start_time = time.time()
    logger.info("Début du traitement de la requête /match")
    
    try:
        # Lecture et validation de l'image
        image_bytes = await file.read()
        if not validate_image_file(image_bytes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
        
        # Traitement de l'image
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        
        # Calcul de l'embedding
        embedding = get_embedding(model, img)
        
        # Recherche des correspondances
        logger.info(f"Embedding calculé. Recherche des meilleures correspondances parmi {len(reference_embeddings)} références")
        matches = get_top_matches(embedding)
        logger.info(f"Correspondances trouvées: {matches}")
        
        # Convertir les correspondances pour assurer la compatibilité avec le modèle Pydantic
        formatted_matches = []
        for match in matches:
            # Créer un nouveau dictionnaire avec la clé 'class_' au lieu de 'class'
            formatted_match = {
                'class_': match.get('class', ''),
                'similarity': match.get('similarity', 0.0)
            }
            formatted_matches.append(formatted_match)
        
        # Calcul du temps de traitement
        processing_time = time.time() - start_time
        
        # Enregistrement des métriques temporaires (non validées)
        best_match = matches[0] if matches else {"class": "unknown", "similarity": 0.0}
        monitor.add_temp_prediction({
            'timestamp': datetime.now(),
            'predicted_label': best_match["class"],
            'confidence': float(best_match["similarity"]),
            'embedding': embedding.flatten().tolist(),
            'processing_time': processing_time
        })
        
        log_security_event(
            "PREDICTION_SUCCESS",
            f"Successful prediction for user {current_user}"
        )
        
        return {"matches": formatted_matches}
        
    except Exception as e:
        log_security_event(
            "PREDICTION_ERROR",
            f"Error during prediction: {str(e)}",
            "ERROR"
        )
        logger.error(f"Erreur lors du traitement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de l'image: {str(e)}"
        )

@app.post("/validate_prediction", response_model=ValidationResponse, summary="Valider une prédiction", description="Permet de valider une prédiction et de l'ajouter aux métriques")
@limiter.limit("10/minute")
async def validate_prediction(
    request: Request,
    validation: PredictionValidation,
    current_user: str = Depends(get_current_user)
):
    """
    Valide une prédiction et l'ajoute aux métriques
    """
    try:
        logger.info(f"[API] Réception d'une demande de validation pour la classe: {validation.predicted_class}")
        
        # Ajouter la prédiction validée aux métriques
        logger.info("[API] Tentative de validation via le moniteur")
        success = monitor.validate_last_prediction(validation.predicted_class)
        
        if not success:
            return {
                "status": "warning",
                "message": "Aucune prédiction récente à valider"
            }
            
        logger.info(f"[API] Prédiction validée pour la classe: {validation.predicted_class}")
        
        # Générer et sauvegarder le rapport avec les prédictions validées
        logger.info("[API] Génération du rapport")
        metrics = monitor.generate_report()
        
        log_security_event(
            "VALIDATION_SUCCESS",
            f"Prediction validated by user {current_user}"
        )
        
        if metrics:
            logger.info(f"[API] Rapport généré avec {metrics['n_predictions']} prédictions au total")
        else:
            logger.warning("[API] Aucune métrique générée")
        
        return {
            "status": "success", 
            "message": "Prédiction validée"
        }
    except Exception as e:
        log_security_event(
            "VALIDATION_ERROR",
            f"Error during validation: {str(e)}",
            "ERROR"
        )
        logger.error(f"[API] Erreur lors de la validation de la prédiction: {str(e)}")
        logger.exception("[API] Détails de l'erreur:")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la validation de la prédiction: {str(e)}"
        )

@app.post("/search_tags", summary="Rechercher des verres par tags", description="Recherche les verres correspondant à une liste de tags")
@limiter.limit("10/minute")
async def search_tags(
    request: Request, 
    tags: List[str] = Body(...), 
    current_user_email: str = Depends(get_current_user)
):
    """
    Recherche les verres correspondant aux tags donnés
    """
    if not tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La liste de tags ne peut pas être vide"
        )
        
    logger.info(f"Recherche pour les tags: {tags}")
    results = find_matching_verres(tags)
    logger.info(f"Trouvé {len(results)} résultats")
    
    return {"results": results}

@app.get("/verre/{verre_id}", summary="Obtenir les détails d'un verre", description="Récupère les détails complets d'un verre par son ID")
@limiter.limit("20/minute")
async def get_verre(
    request: Request, 
    verre_id: int, 
    current_user_email: str = Depends(get_current_user)
):
    """
    Récupère les détails d'un verre par son ID
    """
    logger.info(f"Recherche du verre avec ID: {verre_id}")
    verre = get_verre_details(verre_id)
    
    if not verre:
        logger.warning(f"Verre avec ID {verre_id} non trouvé")
        return {"error": "Verre non trouvé"}
        
    logger.info(f"Verre trouvé: {verre['nom']}")
    return {"verre": verre}

@app.get("/verre_staging/{verre_id}", summary="Obtenir les détails d'un verre depuis staging", description="Récupère les détails d'un verre depuis la table staging par son ID")
@limiter.limit("20/minute")
async def get_verre_staging(
    request: Request, 
    verre_id: int, 
    current_user_email: str = Depends(get_current_user)
):
    """
    Récupère les détails d'un verre depuis la table staging par son ID.
    Cette table contient des informations supplémentaires comme glass_name.
    """
    logger.info(f"Recherche du verre avec ID {verre_id} dans la table staging")
    verre = get_verre_staging_details(verre_id)
    
    if not verre:
        logger.warning(f"Verre avec ID {verre_id} non trouvé dans staging ou pas d'id_interne")
        return {"verre_staging": {}}
        
    logger.info(f"Verre trouvé dans staging avec glass_name: {verre.get('glass_name', 'Non spécifié')}")
    return {"verre_staging": verre}

# Route de test pour vérifier que l'API fonctionne
@app.get("/")
async def root():
    """Route racine de l'API."""
    return {"message": "Bienvenue sur l'API de classification d'images"}

# Point de terminaison de santé
@app.get("/health")
async def health_check():
    """Vérifie que l'API est en fonctionnement."""
    return {"status": "healthy"} 
