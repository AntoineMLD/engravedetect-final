"""
Package contenant les modèles SQLAlchemy pour l'API.
"""

# Les imports sont faits directement dans les fichiers qui en ont besoin
# pour éviter les imports circulaires

from .verres import Verre

__all__ = ["Verre"]
