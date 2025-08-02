import torch
from torchvision import transforms
from PIL import Image
import sys
import os
from .config import MODEL_WEIGHTS_PATH, IMAGE_SIZE
from models.efficientnet_triplet import EfficientNetEmbedding

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

transform = transforms.Compose(
    [transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)), transforms.ToTensor(), transforms.Normalize(mean=[0.5], std=[0.5])]
)


def load_model():
    """
    Charge le modèle EfficientNetEmbedding avec les poids entraînés pour l'API IA.

    Returns:
        EfficientNetEmbedding: Modèle PyTorch prêt à l'inférence.

    Exemple d'utilisation :
        model = load_model()
    """
    # Nous utilisons pretrained=False car nous chargeons nos propres poids
    # Le warning ne devrait plus apparaître car nous avons modifié la classe pour utiliser weights=None
    model = EfficientNetEmbedding(embedding_dim=256, pretrained=False)
    model.load_state_dict(torch.load(MODEL_WEIGHTS_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model


def preprocess_image(img: Image.Image):
    """
    Prétraite une image PIL pour l'inférence avec le modèle EfficientNetEmbedding.

    Args:
        img (PIL.Image.Image): Image à prétraiter.

    Returns:
        torch.Tensor: Image transformée, normalisée et prête à être passée au modèle.

    Exemple d'utilisation :
        tensor = preprocess_image(img)
    """
    return transform(img).unsqueeze(0).to(DEVICE)


def get_embedding(model, img: Image.Image):
    """
    Extrait l'embedding d'une image à l'aide du modèle fourni.

    Args:
        model: Modèle EfficientNetEmbedding chargé.
        img (PIL.Image.Image): Image à encoder.

    Returns:
        np.ndarray: Vecteur d'embedding de l'image.

    Exemple d'utilisation :
        emb = get_embedding(model, img)
    """
    tensor = preprocess_image(img)
    with torch.no_grad():
        emb = model.forward_one(tensor).cpu().numpy()
    return emb[0]
