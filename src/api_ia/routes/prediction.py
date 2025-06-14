"""
Routes pour les prédictions et la recherche de similarité.
"""

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from PIL import Image
import io
import time
from datetime import datetime
from ..core.security import verify_token, validate_image_file
from ..services.model_service import get_embedding, load_model
from ..services.similarity_service import get_top_matches, load_references
from ..schemas.responses import MatchResponse, ValidationResponse
from ..schemas.requests import PredictionValidation
from ..monitoring.metrics_collector import monitor
from ..main import limiter

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Charger le modèle au démarrage
model = load_model()
load_references(model)


@router.post(
    "/match",
    response_model=MatchResponse,
    summary="Trouver les correspondances pour une image",
)
@limiter.limit("5/minute")
async def get_best_match(
    request: Request,
    file: UploadFile = File(...),
    current_user: str = Depends(oauth2_scheme),
):
    """
    Analyse une image et renvoie les classes les plus similaires.
    """
    start_time = time.time()

    # Vérifier le token
    verify_token(current_user)

    # Lire et valider l'image
    image_bytes = await file.read()
    if not validate_image_file(image_bytes):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    # Traiter l'image
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    embedding = get_embedding(model, img)

    # Trouver les correspondances
    matches = get_top_matches(embedding)

    # Enregistrer les métriques
    processing_time = time.time() - start_time
    best_match = matches[0] if matches else {"class": "unknown", "similarity": 0.0}
    monitor.add_temp_prediction(
        {
            "timestamp": datetime.now(),
            "predicted_label": best_match["class"],
            "confidence": float(best_match["similarity"]),
            "embedding": embedding.flatten().tolist(),
            "processing_time": processing_time,
        }
    )

    return {"matches": matches}


@router.post(
    "/validate_prediction",
    response_model=ValidationResponse,
    summary="Valider une prédiction",
)
@limiter.limit("10/minute")
async def validate_prediction(
    request: Request,
    validation: PredictionValidation,
    current_user: str = Depends(oauth2_scheme),
):
    """
    Valide une prédiction et l'ajoute aux métriques.
    """
    try:
        # Ajouter la prédiction validée aux métriques
        success = monitor.validate_last_prediction(validation.predicted_class)

        if not success:
            return {
                "status": "warning",
                "message": "Aucune prédiction récente à valider",
            }

        # Générer et sauvegarder le rapport
        monitor.generate_report()

        return {"status": "success", "message": "Prédiction validée"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la validation de la prédiction: {str(e)}",
        )
