#src/api_ia/app/config.py
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

# Configuration de la sécurité (utilise les mêmes paramètres que l'API principale)
SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration du modèle
MODEL_WEIGHTS_PATH = "/app/api_ia/weights/efficientnet_triplet.pth"
IMAGE_SIZE = 224

# Configuration des références
REFERENCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "references")
os.makedirs(REFERENCES_DIR, exist_ok=True)

# Configuration du serveur
HOST = "0.0.0.0"
PORT = 8001  # Port pour l'API IA

# Configuration de la base PostgreSQL (Coolify)
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")
DATA_DIR = os.path.join(BASE_DIR, "data")
REFERENCE_DIR = os.path.join(DATA_DIR, "oversampled_gravures")

# Configuration du monitoring
REPORTS_DIR = os.path.join(LOG_DIR, "reports")

# Création des répertoires nécessaires
os.makedirs(REPORTS_DIR, exist_ok=True)

# Vérification des variables d'environnement requises uniquement en production
if os.getenv("ENVIRONMENT") == "production":
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Variables d'environnement manquantes : {', '.join(missing_vars)}")
