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

    # Configuration base de données
    DATABASE_URL: str | None = None

    @computed_field
    @property
    def computed_database_url(self) -> str:
        """Retourne l'URL de connexion à la base PostgreSQL ou SQLite en test."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if IS_TEST:
            return "sqlite:///./test.db"
        raise ValueError("DATABASE_URL must be defined in the .env file")

    # Configuration sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY", "test-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Configuration serveur
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://engravedetect.fr")

    # Configuration OpenAPI/Swagger
    OPENAPI_URL: str = os.getenv("OPENAPI_URL", "/openapi.json")
    DOCS_URL: str = os.getenv("DOCS_URL", "/docs")
    REDOC_URL: str = os.getenv("REDOC_URL", "/redoc")
    API_DESCRIPTION: str = "API de gestion des verres optiques"

    # Docker Hub
    docker_hub_username: str | None = os.getenv("DOCKER_HUB_USERNAME")
    docker_hub_token: str | None = os.getenv("DOCKER_HUB_TOKEN")

    # Admin
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")

    # CSRF
    csrf_secret_key: str = os.getenv("CSRF_SECRET_KEY", "default-csrf-secret-key")
    csrf_token_expire_minutes: str = os.getenv("CSRF_TOKEN_EXPIRE_MINUTES", "60")

    # CORS / Sécurité réseau
    allowed_hosts: str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    # Déploiement
    deploy_ssh_key: str = os.getenv("DEPLOY_SSH_KEY", "")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    reports_dir: str = os.getenv("REPORTS_DIR", "/app/logs/reports")

    # Monitoring Grafana
    grafana_token: str = os.getenv("GRAFANA_TOKEN", "")
    grafana_host: str = os.getenv("GRAFANA_HOST", "")

    model_config = ConfigDict(env_file=".env", extra="allow")


settings = Settings()


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
