"""
Service for model loading and inference.
"""

import torch
from torchvision import transforms
from PIL import Image
from ..core.config import MODEL_WEIGHTS_PATH, IMAGE_SIZE
from models.efficientnet_triplet import EfficientNetEmbedding

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

transform = transforms.Compose(
    [
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]),
    ]
)


def load_model():
    model = EfficientNetEmbedding(embedding_dim=256, pretrained=False)
    model.load_state_dict(torch.load(MODEL_WEIGHTS_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model


def preprocess_image(img: Image.Image):
    return transform(img).unsqueeze(0).to(DEVICE)


def get_embedding(model, img: Image.Image):
    tensor = preprocess_image(img)
    with torch.no_grad():
        emb = model.forward_one(tensor).cpu().numpy()
    return emb[0]
