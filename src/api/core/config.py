import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # Nom et version de l'application
    APP_NAME: str = "EngraveDetect API"
    APP_VERSION: str = "1.0.0"

    # Configuration de l'API
    API_V1_STR: str = "/api/v1"

    # Configuration de la base de données
    DATABASE_URL: str = "sqlite:///./test.db"  # Valeur par défaut pour les tests

    # Configuration Azure
    AZURE_SERVER: str = "test-server"  # Valeur par défaut pour les tests
    AZURE_DATABASE: str = "test-db"    # Valeur par défaut pour les tests
    AZURE_USERNAME: str = "test-user"  # Valeur par défaut pour les tests
    AZURE_PASSWORD: str = "test-password"  # Valeur par défaut pour les tests

    # Configuration Docker Hub
    docker_hub_username: str | None = None
    docker_hub_token: str | None = None

    # Configuration de sécurité
    SECRET_KEY: str = "test-secret-key-for-testing-only"  # Valeur par défaut pour les tests
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configuration du serveur
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Configuration OpenAPI/Swagger
    OPENAPI_URL: str = "/openapi.json"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    # Description de l'API
    API_DESCRIPTION: str = """
    API REST pour la gestion des verres optiques.
    """

    model_config = ConfigDict(env_file=".env")


settings = Settings()

# Configuration OpenAPI pour Swagger/ReDoc
openapi_config = {
    "title": settings.APP_NAME,
    "version": settings.APP_VERSION,
    "description": settings.API_DESCRIPTION,
    "openapi_tags": [
        {
            "name": "verres",
            "description": "Opérations sur les verres optiques"
        },
        {
            "name": "auth",
            "description": "Authentification et gestion des tokens"
        }
    ],
    "docs_url": settings.DOCS_URL,
    "openapi_url": settings.OPENAPI_URL,
    "redoc_url": settings.REDOC_URL
}
