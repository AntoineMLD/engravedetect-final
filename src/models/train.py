"""
Script d'entraînement du modèle EfficientNet avec Triplet Loss.

Ce module entraîne le modèle EfficientNetEmbedding pour la classification
des gravures sur les verres optiques en utilisant la Triplet Loss.

Fonctionnalités :
- Chargement et préparation du dataset de triplets
- Configuration du modèle EfficientNet avec embedding
- Entraînement avec Triplet Loss (semi-hard mining)
- Sauvegarde du modèle entraîné
- Génération de courbes de perte

Paramètres d'entraînement :
- Embedding dimension : 256
- Margin : 0.3
- Batch size : 32
- Nombre d'époques : 20
- Learning rate : 1e-4

Auteur : Équipe de développement
Version : 1.0.0
"""

import os
import sys
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm import tqdm
import matplotlib.pyplot as plt
from efficientnet_triplet import EfficientNetEmbedding
from losses.triplet_losses import HardTripletLoss
from datasets.triplet_dataset import TripletDataset, default_transform

# --- Configuration globale ---
main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(main_dir)

DATA_DIR = os.path.join(main_dir, "data", "split", "train")
SAVE_PATH = os.path.join(main_dir, "models", "efficientnet_triplet.pth")
PLOT_PATH = os.path.join(main_dir, "reports", "training_loss.png")

EMBEDDING_DIM = 256
MARGIN = 0.3
BATCH_SIZE = 32
NUM_EPOCHS = 20
LEARNING_RATE = 1e-4
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- Dataset & DataLoader ---
# Chargement du dataset de triplets pour l'entraînement.
# Chaque échantillon est un triplet (anchor, positive, negative).
dataset = TripletDataset(root_dir=DATA_DIR, transform=default_transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
print(f"Dataset chargé : {len(dataset)} triplets disponibles")

# --- Modèle ---
# Instanciation du modèle EfficientNet pour l'extraction d'embeddings.
model = EfficientNetEmbedding(embedding_dim=EMBEDDING_DIM, pretrained=True)
model = model.to(DEVICE)
print(f"Modèle EfficientNet prêt sur {DEVICE}")

# --- Fonction de perte et optimiseur ---
# Utilisation de la Triplet Loss avec mining semi-hard.
criterion = HardTripletLoss(margin=MARGIN, mining_type="semi-hard")
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# --- Entraînement ---
model.train()
train_losses = []

for epoch in range(NUM_EPOCHS):
    """
    Boucle principale d'entraînement sur NUM_EPOCHS époques.
    À chaque époque :
    - Parcours de tous les triplets du DataLoader
    - Calcul des embeddings et de la perte
    - Rétropropagation et mise à jour des poids
    - Suivi de la perte moyenne pour affichage et analyse
    """
    epoch_loss = 0.0
    progress_bar = tqdm(dataloader, desc=f"📚 Epoch {epoch + 1}/{NUM_EPOCHS}")

    for anchor, positive, negative in progress_bar:
        anchor = anchor.to(DEVICE)
        positive = positive.to(DEVICE)
        negative = negative.to(DEVICE)

        # 1. Forward : calcul des embeddings pour chaque image du triplet
        anchor_emb, pos_emb, neg_emb = model(anchor, positive, negative)

        # 2. Loss : calcul de la Triplet Loss
        loss = criterion(anchor_emb, pos_emb, neg_emb)

        # 3. Backward : rétropropagation et mise à jour des poids
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 4. Statistiques : suivi de la perte pour affichage
        epoch_loss += loss.item()
        progress_bar.set_postfix(loss=loss.item())

    avg_loss = epoch_loss / len(dataloader)
    train_losses.append(avg_loss)
    print(f"Epoch {epoch + 1} terminée - Loss moyenne : {avg_loss:.4f}")

# --- Sauvegarde du modèle ---
# Enregistre les poids du modèle entraîné pour une utilisation ultérieure.
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
torch.save(model.state_dict(), SAVE_PATH)
print(f"Modèle sauvegardé dans : {SAVE_PATH}")

# --- Courbe de perte ---
# Génère et sauvegarde la courbe de perte d'entraînement pour analyse.
plt.figure(figsize=(10, 5))
plt.plot(train_losses, marker="o", color="royalblue")
plt.title("Courbe de perte (Training Loss)")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.grid(True)
plt.tight_layout()

os.makedirs(os.path.dirname(PLOT_PATH), exist_ok=True)
plt.savefig(PLOT_PATH)
print(f"Courbe de perte sauvegardée dans : {PLOT_PATH}")
