"""
Module de dataset pour l'entraînement avec Triplet Loss.

Ce module contient la classe TripletDataset qui génère dynamiquement des triplets
d'images (anchor, positive, negative) pour l'entraînement de modèles de deep learning
utilisant la Triplet Loss.

Fonctionnalités :
- Génération automatique de triplets d'images
- Sélection intelligente d'images positives et négatives
- Support des transformations d'images
- Gestion des formats d'images multiples (PNG, JPG, JPEG)
- Conversion automatique en grayscale

Structure des triplets :
- Anchor : Image de référence
- Positive : Image de la même classe que l'anchor
- Negative : Image d'une classe différente

Transformations par défaut :
- Redimensionnement à 224x224 pixels
- Conversion en tenseur PyTorch
- Normalisation avec mean=0.5, std=0.5

Auteur : Équipe de développement
Version : 1.0.0
"""

import os
import random
from PIL import Image
from typing import Tuple, List
from torch.utils.data import Dataset
import torchvision.transforms as transforms


class TripletDataset(Dataset):
    """
    Dataset PyTorch pour la génération dynamique de triplets d'images (anchor, positive, negative).

    Ce dataset est utilisé pour l'entraînement de modèles avec la Triplet Loss.
    Il sélectionne automatiquement, pour chaque image ancre, une image positive (même classe)
    et une image négative (classe différente).

    Args:
        root_dir (str): Dossier racine contenant les sous-dossiers de classes.
        transform (callable, optionnel): Transformations à appliquer aux images.

    Exemple d'utilisation :
        dataset = TripletDataset('data/split/train', transform=default_transform)
        anchor, positive, negative = dataset[0]
    """
    def __init__(self, root_dir: str, transform=None):
        """
        Initialise le dataset de triplets à partir d'un dossier racine.

        Args:
            root_dir (str): Dossier racine contenant les sous-dossiers de classes.
            transform (callable, optionnel): Transformations à appliquer aux images.
        """
        self.root_dir = root_dir
        self.transform = transform

        # D'abord, on liste les classes disponibles
        self.classes = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}

        # Ensuite, construire un dictionnaire {classe: [liste des chemins d'images]}
        self.image_dict = {}
        for cls in self.classes:
            class_path = os.path.join(root_dir, cls)
            images = [
                os.path.join(class_path, f) for f in os.listdir(class_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
            if len(images) >= 2:
                self.image_dict[cls] = images

        # Générer une liste plate d'images disponibles
        self.samples = [(img_path, cls) for cls, imgs in self.image_dict.items() for img_path in imgs]

    def __len__(self):
        """
        Retourne le nombre total de triplets disponibles dans le dataset.

        Returns:
            int: Nombre de triplets (égal au nombre d'images disponibles).
        """
        return len(self.samples)

    def __getitem__(self, index: int) -> Tuple:
        """
        Retourne un triplet (anchor, positive, negative) pour l'index donné.

        Args:
            index (int): Index du triplet à retourner.

        Returns:
            Tuple: (anchor, positive, negative), chacun étant une image (PIL ou Tensor).

        Exemple d'utilisation :
            anchor, positive, negative = dataset[0]
        """
        anchor_path, anchor_class = self.samples[index]

        # Tirer une image positive dans la même classe (différente de l'ancre)
        positive_candidates = [p for p in self.image_dict[anchor_class] if p != anchor_path]
        positive_path = random.choice(positive_candidates)

        # Tire une classe négative (différente de l'ancre et de la positive)
        negative_class = random.choice([c for c in self.classes if c != anchor_class])
        negative_path = random.choice(self.image_dict[negative_class])

        # Charger les images
        anchor = Image.open(anchor_path).convert("L")
        positive = Image.open(positive_path).convert("L")
        negative = Image.open(negative_path).convert("L")

        # Appliquer les transformations si elles existent
        if self.transform:
            anchor = self.transform(anchor)
            positive = self.transform(positive)
            negative = self.transform(negative)

        return anchor, positive, negative


default_transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),  # convertit en (1, H, W) pour grayscale
        transforms.Normalize(mean=[0.5], std=[0.5]),  # standardisation classique
    ]
)
