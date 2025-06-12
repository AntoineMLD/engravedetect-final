"""
Package contenant les modèles SQLAlchemy pour l'API.
"""

# Les imports sont faits directement dans les fichiers qui en ont besoin
# pour éviter les imports circulaires

from .verres import Verre
from .references import Fournisseur, Materiau, Gamme, Serie

__all__ = [
    'Verre',
    'Fournisseur',
    'Materiau',
    'Gamme',
    'Serie'
]
