from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from PIL import Image
import torch
from api_ia.app.model_loader import preprocess_image
from api_ia.app.config import REFERENCE_DIR

reference_embeddings = []


def load_references(model):
    """
    Cette fonction permet donc de créer une base de données d'embeddings de référence
    qui pourra être utilisée plus tard pour comparer des images inconnues aux
    images de référence par similarité.
    """
    if not os.path.exists(REFERENCE_DIR):
        raise FileNotFoundError(f"Le répertoire de référence {REFERENCE_DIR} n'existe pas")

    for cls in os.listdir(REFERENCE_DIR):
        path = os.path.join(REFERENCE_DIR, cls, f"{cls}.png")
        if not os.path.exists(path):
            continue
        img = Image.open(path).convert("L")
        tensor = preprocess_image(img)
        with torch.no_grad():  # indique de ne pas calculer les gradients, économise des ressources
            emb = model.forward_one(tensor).cpu().numpy()[0]
        reference_embeddings.append((cls, emb))


def get_top_matches(query_emb, k=5):
    """
    Cette fonction permet de trouver les k images de référence les plus similaires
    à l'image inconnue.
    """
    scores = []
    for cls, ref_emb in reference_embeddings:
        sim = cosine_similarity([query_emb], [ref_emb])[0][
            0
        ]
        #  La similarité cosinus est une mesure de similarité entre deux vecteurs qui varie de -1 (complètement différent) à 1 (identique).
        scores.append((cls, sim))
    top = sorted(scores, key=lambda x: x[1], reverse=True)[:k]
    return [{"class": c, "similarity": float(s)} for c, s in top]
