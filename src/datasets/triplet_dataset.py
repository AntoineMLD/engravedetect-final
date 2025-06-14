import os
import random
from PIL import Image
from typing import Tuple, List
from torch.utils.data import Dataset
import torchvision.transforms as transforms

class TripletDataset(Dataset):
    def __init__(self, root_dir:str, transform=None):
        """
        Dataset qui génère dynamiquement des triplets d'images pour l'entrainement d'un modèle de triplet.

        Args:
            root_dir: Dossier racine contenant les sous-dossiers de classes
            transform: Transformations à appliquer aux images (par ex. redimensionnement)
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
                os.path.join(class_path, f) for f in os.listdir(class_path)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
            ]
            if len(images) >= 2:
                self.image_dict[cls] = images

        # Générer une liste plate d'images disponibles 
        self.samples = [(img_path, cls) for cls, imgs in self.image_dict.items() for img_path in imgs]


    def __len__(self):
        return len(self.samples)


    def __getitem__(self, index: int) -> Tuple:
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


default_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),  # convertit en (1, H, W) pour grayscale
    transforms.Normalize(mean=[0.5], std=[0.5])  # standardisation classique
])   
