"""
Middleware de sécurité pour l'API FastAPI.
Implémente des en-têtes de sécurité HTTP recommandés.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui ajoute des en-têtes de sécurité HTTP à toutes les réponses.

    Les en-têtes ajoutés incluent :
    - Content-Security-Policy : Contrôle les ressources pouvant être chargées
    - X-Content-Type-Options : Empêche le MIME-sniffing
    - X-Frame-Options : Protection contre le clickjacking
    - X-XSS-Protection : Protection contre les attaques XSS
    - Strict-Transport-Security : Force l'utilisation de HTTPS
    - Referrer-Policy : Contrôle les informations de référence
    - Permissions-Policy : Contrôle les fonctionnalités du navigateur
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # En-têtes de sécurité de base
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy adaptée pour Swagger UI
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self';"
        )
        response.headers["Content-Security-Policy"] = csp

        # Permissions Policy
        permissions_policy = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )
        response.headers["Permissions-Policy"] = permissions_policy

        return response
