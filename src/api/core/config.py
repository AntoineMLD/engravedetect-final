from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Settings(BaseSettings):
    # Nom et version de l'application
    APP_NAME: str = "EngraveDetect API"
    APP_VERSION: str = "1.0.0"

    # Configuration de l'API
    API_V1_STR: str = "/api/v1"

    # Configuration de la base de données
    DATABASE_URL: str

    # Configuration Azure
    AZURE_SERVER: str
    AZURE_DATABASE: str
    AZURE_USERNAME: str
    AZURE_PASSWORD: str

    @field_validator("AZURE_SERVER", "AZURE_DATABASE", "AZURE_USERNAME", "AZURE_PASSWORD", "DATABASE_URL")
    @classmethod
    def validate_azure_config(cls, v: str, info) -> str:
        if not v:
            raise ValueError(f"{info.field_name} ne peut pas être vide")
        return v

    @property
    def DATABASE_URL(self) -> str:
        """Construit la chaîne de connexion ODBC pour Azure SQL Server."""
        return (
            f"mssql+pyodbc://{self.AZURE_USERNAME}:{self.AZURE_PASSWORD}@"
            f"{self.AZURE_SERVER}/{self.AZURE_DATABASE}?"
            "driver=ODBC+Driver+18+for+SQL+Server&"
            "TrustServerCertificate=yes&"
            "Connection Timeout=30"
        )

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
    API_DESCRIPTION: str = "API de gestion des verres optiques"

    # Configuration du déploiement
    deploy_ssh_key: str = ""  # Utiliser une chaîne vide comme valeur par défaut

    model_config = ConfigDict(env_file=".env")


settings = Settings()

# Configuration OpenAPI pour Swagger/ReDoc
openapi_config = {
    "title": settings.APP_NAME,
    "version": settings.APP_VERSION,
    "description": settings.API_DESCRIPTION,
    "openapi_tags": [
        {"name": "verres", "description": "Opérations sur les verres optiques"},
        {"name": "auth", "description": "Authentification et gestion des tokens"},
    ],
    "docs_url": settings.DOCS_URL,
    "openapi_url": settings.OPENAPI_URL,
    "redoc_url": settings.REDOC_URL,
}
