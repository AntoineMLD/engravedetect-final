"""
Configuration centralisée pour l'API

Centralise les paramètres de configuration de l'API pour faciliter
la maintenance et les modifications.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration des logs
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configuration de l'API
API_TITLE = "API IA pour la Classification des Verres"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
API pour la classification des verres utilisant un modèle d'IA.
Fournit des endpoints pour l'analyse d'images et la recherche de correspondances.
"""

# Configuration de la sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ROTATION_THRESHOLD_MINUTES = 5

# Configuration du modèle
MODEL_WEIGHTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "weights", "model.pth")
IMAGE_SIZE = 224

# Configuration des références
REFERENCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "references")
os.makedirs(REFERENCES_DIR, exist_ok=True)

# Configuration des utilisateurs
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Configuration du serveur
HOST = "0.0.0.0"
PORT = 8001  # Port pour l'API IA

# Configuration de sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ROTATION_THRESHOLD_MINUTES = int(os.getenv("ROTATION_THRESHOLD_MINUTES", "25"))

# Configuration d'authentification
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")
DATA_DIR = os.path.join(BASE_DIR, "data")
REFERENCE_DIR = os.path.join(DATA_DIR, "oversampled_gravures")

# Configuration Azure Database
AZURE_SERVER = os.getenv("AZURE_SERVER", "")
AZURE_DATABASE = os.getenv("AZURE_DATABASE", "")
AZURE_USERNAME = os.getenv("AZURE_USERNAME", "")
AZURE_PASSWORD = os.getenv("AZURE_PASSWORD", "")
AZURE_DRIVER = "{ODBC Driver 18 for SQL Server}"

# Configuration du monitoring
REPORTS_DIR = os.path.join(LOG_DIR, "reports")

# Création des répertoires nécessaires
os.makedirs(REPORTS_DIR, exist_ok=True)

# Vérification des variables d'environnement requises
required_vars = [
    "AZURE_SERVER",
    "AZURE_DATABASE",
    "AZURE_USERNAME",
    "AZURE_PASSWORD",
    "SECRET_KEY",
    "ADMIN_EMAIL",
    "ADMIN_PASSWORD",
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Variables d'environnement manquantes : {', '.join(missing_vars)}")
