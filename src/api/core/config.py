from pydantic_settings import BaseSettings
from pydantic import ConfigDict, computed_field
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Déterminer si nous sommes en mode test
IS_TEST = os.getenv("ENVIRONMENT") == "test"


class Settings(BaseSettings):
    # Nom et version de l'application
    APP_NAME: str = "EngraveDetect API"
    APP_VERSION: str = "1.0.0"

    # Configuration SMTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.example.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))  # 465 pour SSL, 587 pour STARTTLS
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "user@example.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "password")
    SMTP_SENDER: str = os.getenv("SMTP_SENDER", "noreply@example.com")
    
    # Configuration de l'API
    API_V1_STR: str = "/api/v1"

    # Configuration Azure
    AZURE_SERVER: str = "test-server" if IS_TEST else os.getenv("AZURE_SERVER", "test-server")
    AZURE_DATABASE: str = "test-db" if IS_TEST else os.getenv("AZURE_DATABASE", "test-db")
    AZURE_USERNAME: str = "test-user" if IS_TEST else os.getenv("AZURE_USERNAME", "test-user")
    AZURE_PASSWORD: str = "test-password" if IS_TEST else os.getenv("AZURE_PASSWORD", "test-password")

    # Champs supplémentaires trouvés dans votre .env
    database_url: str | None = None  # Permet de surcharger via .env
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123"
    csrf_secret_key: str = "default-csrf-secret-key"
    csrf_token_expire_minutes: str = "60"
    allowed_hosts: str = "localhost,127.0.0.1"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @computed_field
    @property
    def computed_database_url(self) -> str:
        """Construit la chaîne de connexion ODBC pour Azure SQL Server."""
        # Si database_url est défini dans .env, l'utiliser
        if self.database_url:
            return self.database_url

        # En mode test, utiliser SQLite
        if IS_TEST:
            return "sqlite:///./test.db"

        # En production, construire depuis les paramètres Azure
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

    # AJOUT IMPORTANT : Permettre les champs extra
    model_config = ConfigDict(env_file=".env", extra="allow")  # Permet les champs supplémentaires


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


