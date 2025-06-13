"""
Configuration settings for the API.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# API Information
API_TITLE = "API de Classification des Verres"
API_VERSION = "1.0.0"
API_DESCRIPTION = "API pour la classification des verres et la recherche de similarité"

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # À remplacer en production
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Model Configuration
IMAGE_SIZE = 224
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEIGHTS_DIR = os.path.join(BASE_DIR, "models", "weights")
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "efficientnet_triplet.pth")
REFERENCE_DIR = os.path.join(DATA_DIR, "split", "train")

# Monitoring Configuration
LOG_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(LOG_DIR, "reports")

# Security
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Création des répertoires nécessaires
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(WEIGHTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
