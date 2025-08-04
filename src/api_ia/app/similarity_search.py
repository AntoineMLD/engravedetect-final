import logging
import os

import numpy as np
import torch
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

from api_ia.app.config import REFERENCE_DIR
from api_ia.app.model_loader import preprocess_image

logger = logging.getLogger(__name__)
reference_embeddings = []


def load_references(model):
    """
    Charge les embeddings de référence à partir des images de référence du dossier REFERENCE_DIR.

    Cette fonction parcourt chaque classe dans le dossier de référence, charge l'image PNG correspondante,
    calcule son embedding et stocke le résultat dans la variable globale reference_embeddings.

    Args:
        model: Modèle EfficientNetEmbedding chargé pour l'extraction d'embeddings.

    Raises:
        FileNotFoundError: Si le dossier de référence n'existe pas.

    Exemple d'utilisation :
        load_references(model)
    """
    global reference_embeddings
    reference_embeddings = []  # Reset

    if not os.path.exists(REFERENCE_DIR):
        raise FileNotFoundError(f"Le répertoire de référence {REFERENCE_DIR} n'existe pas")

    logger.info(f"Chargement des références depuis {REFERENCE_DIR}")

    for cls in os.listdir(REFERENCE_DIR):
        path = os.path.join(REFERENCE_DIR, cls, f"{cls}.png")
        logger.info(f"Recherche du fichier: {path}")

        if not os.path.exists(path):
            logger.warning(f"Fichier non trouvé: {path}")
            continue

        try:
            img = Image.open(path).convert("L")
            tensor = preprocess_image(img)
            with torch.no_grad():  # indique de ne pas calculer les gradients, économise des ressources
                emb = model.forward_one(tensor).cpu().numpy()[0]
            reference_embeddings.append((cls, emb))
            logger.info(f"Référence chargée: {cls}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {cls}: {e}")

    logger.info(f"Total des références chargées: {len(reference_embeddings)}")


def get_top_matches(query_emb, k=20):
    """
    Trouve les k images de référence les plus similaires à l'embedding fourni.

    Args:
        query_emb (np.ndarray): Embedding de l'image requête.
        k (int): Nombre de résultats à retourner (top-k).

    Returns:
        List[Dict]: Liste des k classes les plus similaires avec leur score de similarité.

    Exemple d'utilisation :
        top_matches = get_top_matches(query_emb, k=5)
    """
    if not reference_embeddings:
        logger.warning("Aucune référence chargée!")
        return []

    scores = []
    for cls, ref_emb in reference_embeddings:
        sim = cosine_similarity([query_emb], [ref_emb])[0][0]
        #  La similarité cosinus est une mesure de similarité entre deux vecteurs qui varie de -1 (complètement différent) à 1 (identique).
        scores.append((cls, sim))
    top = sorted(scores, key=lambda x: x[1], reverse=True)[:k]
    logger.info(f"Top {k} résultats: {top}")
    return [{"class": c, "similarity": float(s)} for c, s in top]
