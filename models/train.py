import os
import sys
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import matplotlib.pyplot as plt
from models.efficientnet_triplet import EfficientNetEmbedding
from models.losses.triplet_losses import HardTripletLoss
from data.datasets.triplet_dataset import TripletDataset, default_transform

# Ajout du répertoire parent au chemin Python (si lancé depuis models/train.py par ex.)
main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(main_dir)

# --- Configuration globale ---
DATA_DIR = os.path.join(main_dir, "data", "split", "train")
SAVE_PATH = os.path.join(main_dir, "models", "weights", "efficientnet_triplet.pth")
PLOT_PATH = os.path.join(main_dir, "reports", "training_loss.png")

EMBEDDING_DIM = 256
MARGIN = 0.3
BATCH_SIZE = 32
NUM_EPOCHS = 20
LEARNING_RATE = 1e-4
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- Dataset & DataLoader ---
dataset = TripletDataset(root_dir=DATA_DIR, transform=default_transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
print(f"Dataset chargé : {len(dataset)} triplets disponibles")

# --- Modèle ---
model = EfficientNetEmbedding(embedding_dim=EMBEDDING_DIM, pretrained=True)
model = model.to(DEVICE)
print(f"Modèle EfficientNet prêt sur {DEVICE}")

# --- Fonction de perte et optimiseur ---
criterion = HardTripletLoss(margin=MARGIN, mining_type="semi-hard")
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# --- Entraînement ---
model.train()
train_losses = []

for epoch in range(NUM_EPOCHS):
    epoch_loss = 0.0
    progress_bar = tqdm(dataloader, desc=f"📚 Epoch {epoch+1}/{NUM_EPOCHS}")

    for anchor, positive, negative in progress_bar:
        anchor = anchor.to(DEVICE)
        positive = positive.to(DEVICE)
        negative = negative.to(DEVICE)

        # 1. Forward
        anchor_emb, pos_emb, neg_emb = model(anchor, positive, negative)

        # 2. Loss
        loss = criterion(anchor_emb, pos_emb, neg_emb)

        # 3. Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 4. Stat
        epoch_loss += loss.item()
        progress_bar.set_postfix(loss=loss.item())

    avg_loss = epoch_loss / len(dataloader)
    train_losses.append(avg_loss)
    print(f"Epoch {epoch+1} terminée - Loss moyenne : {avg_loss:.4f}")

# --- Sauvegarde du modèle ---
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
torch.save(model.state_dict(), SAVE_PATH)
print(f"Modèle sauvegardé dans : {SAVE_PATH}")

# --- Courbe de perte ---
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
