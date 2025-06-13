"""
Configuration OpenAPI pour FastAPI.
"""

import os
import yaml


def get_openapi_schema():
    """
    Charge le schéma OpenAPI depuis le fichier YAML.
    """
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../docs"))
    openapi_path = os.path.join(docs_dir, "openapi.yaml")

    if not os.path.exists(openapi_path):
        return None

    with open(openapi_path, "r", encoding="utf-8") as f:
        yaml_content = f.read()
        return yaml.safe_load(yaml_content)


def setup_openapi(app):
    """
    Configure FastAPI pour utiliser le schéma OpenAPI personnalisé.
    """
    schema = get_openapi_schema()
    if schema:

        def custom_openapi():
            return schema

        app.openapi = custom_openapi
