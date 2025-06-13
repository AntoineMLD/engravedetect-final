# evaluate_model.py
# Version enrichie avec courbe de top-k accuracy + matrice de confusion

import os
import sys
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# Config
main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(main_dir)

from models.efficientnet_triplet import EfficientNetEmbedding

MODEL_PATH = os.path.join(main_dir, "models", "weights", "efficientnet_triplet.pth")
REFERENCE_DIR = os.path.join(main_dir, "data", "split", "train")  # base de référence
TEST_DIR = os.path.join(main_dir, "data", "split", "test")  # jeu d'évaluation
PLOT_TOPK_PATH = os.path.join(main_dir, "reports", "topk_accuracy.png")
PLOT_CONFMAT_PATH = os.path.join(main_dir, "reports", "confusion_matrix.png")

EMBEDDING_DIM = 256
IMAGE_SIZE = 224
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TOP_KS = [1, 3, 5]

transform = transforms.Compose(
    [
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]),
    ]
)


def load_model():
    model = EfficientNetEmbedding(embedding_dim=EMBEDDING_DIM, pretrained=False)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model


def extract_embeddings(model, data_dir):
    embeddings = []
    labels = []
    paths = []

    for cls in os.listdir(data_dir):
        class_path = os.path.join(data_dir, cls)
        if not os.path.isdir(class_path):
            continue

        for fname in os.listdir(class_path):
            if fname.lower().endswith(("png", "jpg", "jpeg")):
                fpath = os.path.join(class_path, fname)
                img = Image.open(fpath).convert("L")
                tensor = transform(img).unsqueeze(0).to(DEVICE)
                with torch.no_grad():
                    emb = model.forward_one(tensor).cpu().numpy()[0]
                embeddings.append(emb)
                labels.append(cls)
                paths.append(fpath)
    return np.array(embeddings), labels, paths


def compute_topk_accuracy(test_embeddings, test_labels, ref_embeddings, ref_labels, ks):
    similarities = cosine_similarity(test_embeddings, ref_embeddings)
    topk_hits = {k: 0 for k in ks}
    y_true, y_pred_top1 = [], []

    for i, sim_row in enumerate(similarities):
        sorted_idx = np.argsort(sim_row)[::-1]  # descending
        sorted_labels = [ref_labels[j] for j in sorted_idx]

        y_true.append(test_labels[i])
        y_pred_top1.append(sorted_labels[0])

        for k in ks:
            if test_labels[i] in sorted_labels[:k]:
                topk_hits[k] += 1

    topk_acc = {f"Top-{k}": topk_hits[k] / len(test_labels) for k in ks}
    return topk_acc, y_true, y_pred_top1


def plot_topk(topk_acc):
    labels = list(topk_acc.keys())
    values = list(topk_acc.values())

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color="cornflowerblue")
    plt.ylim(0, 1)
    plt.title("Top-k Accuracy sur test set")
    plt.ylabel("Accuracy")
    plt.tight_layout()
    os.makedirs(os.path.dirname(PLOT_TOPK_PATH), exist_ok=True)
    plt.savefig(PLOT_TOPK_PATH)
    print(f"Top-k accuracy sauvegardée : {PLOT_TOPK_PATH}")


def plot_confusion(y_true, y_pred):
    labels = sorted(list(set(y_true + y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    fig, ax = plt.subplots(figsize=(10, 10))
    disp.plot(ax=ax, xticks_rotation=45, cmap="Blues", colorbar=False)
    plt.title("Matrice de confusion (Top-1)")
    plt.tight_layout()
    plt.savefig(PLOT_CONFMAT_PATH)
    print(f"Matrice de confusion sauvegardée : {PLOT_CONFMAT_PATH}")


def main():
    print("Chargement du modèle...")
    model = load_model()

    print("Chargement des embeddings de référence...")
    ref_embeddings, ref_labels, _ = extract_embeddings(model, REFERENCE_DIR)

    print("Chargement des embeddings de test...")
    test_embeddings, test_labels, _ = extract_embeddings(model, TEST_DIR)

    print("Calcul des top-k accuracies...")
    topk_acc, y_true, y_pred = compute_topk_accuracy(test_embeddings, test_labels, ref_embeddings, ref_labels, TOP_KS)
    for k, v in topk_acc.items():
        print(f"{k} Accuracy : {v:.4f}")

    print("Génération des graphiques...")
    plot_topk(topk_acc)
    plot_confusion(y_true, y_pred)


if __name__ == "__main__":
    main()
