"""
Routes d'authentification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..core.security import create_access_token, log_security_event
from ..core.config import ADMIN_EMAIL, ADMIN_PASSWORD
from ..schemas.responses import TokenResponse

router = APIRouter()


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Obtenir un token d'authentification",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Point de terminaison pour l'authentification
    """
    try:
        # Vérifier si l'email et le mot de passe correspondent
        if form_data.username != ADMIN_EMAIL or form_data.password != ADMIN_PASSWORD:
            log_security_event(
                "LOGIN_FAILED",
                f"Failed login attempt for {form_data.username}",
                "WARNING",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Créer le token
        access_token, version = create_access_token(form_data.username)

        log_security_event("LOGIN_SUCCESS", f"Successful login for {form_data.username}")

        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError as e:
        log_security_event(
            "LOGIN_VALIDATION_ERROR",
            f"Validation error during login: {str(e)}",
            "WARNING",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
