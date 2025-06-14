"""
Configuration OpenAPI pour FastAPI
Ce module permet de configurer FastAPI pour utiliser un fichier OpenAPI personnalisé.
"""

import os
import json
import yaml
import logging

logger = logging.getLogger(__name__)


def get_openapi_schema():
    """
    Charge le schéma OpenAPI depuis le fichier YAML
    """
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs"))
    openapi_path = os.path.join(docs_dir, "openapi.yaml")

    if not os.path.exists(openapi_path):
        logger.info("Aucun fichier OpenAPI personnalisé trouvé, utilisation de la configuration par défaut")
        return None

    try:
        with open(openapi_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()
            return yaml.safe_load(yaml_content)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier OpenAPI: {e}")
        return None


def setup_openapi(app):
    """
    Configure FastAPI pour utiliser le schéma OpenAPI personnalisé
    """
    schema = get_openapi_schema()
    if schema:

        def custom_openapi():
            return schema

        app.openapi = custom_openapi
    else:
        # Utiliser la configuration par défaut de FastAPI
        logger.info("Utilisation de la configuration OpenAPI par défaut de FastAPI")
