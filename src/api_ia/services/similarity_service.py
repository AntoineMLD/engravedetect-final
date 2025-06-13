"""
Service for similarity search functionality.
"""

from sklearn.metrics.pairwise import cosine_similarity
import os
from PIL import Image
import torch
from .model_service import preprocess_image
from ..core.config import REFERENCE_DIR

reference_embeddings = []


def load_references(model):
    """
    Charge les embeddings de référence pour la comparaison.
    """
    if not os.path.exists(REFERENCE_DIR):
        raise FileNotFoundError(f"Le répertoire de référence {REFERENCE_DIR} n'existe pas")

    for cls in os.listdir(REFERENCE_DIR):
        path = os.path.join(REFERENCE_DIR, cls, f"{cls}.png")
        if not os.path.exists(path):
            continue
        img = Image.open(path).convert("L")
        tensor = preprocess_image(img)
        with torch.no_grad():
            emb = model.forward_one(tensor).cpu().numpy()[0]
        reference_embeddings.append((cls, emb))


def get_top_matches(query_emb, k=5):
    """
    Trouve les k images de référence les plus similaires.
    """
    scores = []
    for cls, ref_emb in reference_embeddings:
        sim = cosine_similarity([query_emb], [ref_emb])[0][0]
        scores.append((cls, sim))
    top = sorted(scores, key=lambda x: x[1], reverse=True)[:k]
    return [{"class": c, "similarity": float(s)} for c, s in top]
