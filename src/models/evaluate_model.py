"""
Module d'évaluation du modèle EfficientNet pour la classification des gravures
"""

import os
import sys
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.metrics.pairwise import cosine_similarity
from torchvision import transforms

from models.efficientnet_triplet import EfficientNetEmbedding

# Config
main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(main_dir)


MODEL_PATH = os.path.join(main_dir, "models", "efficientnet_triplet.pth")
REFERENCE_DIR = os.path.join(main_dir, "data", "split", "train")  # base de référence
TEST_DIR = os.path.join(main_dir, "data", "split", "test")  # jeu d'évaluation
PLOT_TOPK_PATH = os.path.join(main_dir, "reports", "topk_accuracy.png")
PLOT_CONFMAT_PATH = os.path.join(main_dir, "reports", "confusion_matrix.png")

EMBEDDING_DIM = 256
IMAGE_SIZE = 224
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TOP_KS = [1, 3, 5]

transform = transforms.Compose(
    [transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)), transforms.ToTensor(), transforms.Normalize(mean=[0.5], std=[0.5])]
)


def load_model():
    """
    Charge le modèle EfficientNetEmbedding entraîné depuis le disque.

    Returns:
        EfficientNetEmbedding: Modèle PyTorch prêt à l'évaluation.

    Exemple d'utilisation :
        model = load_model()
    """
    model = EfficientNetEmbedding(embedding_dim=EMBEDDING_DIM, pretrained=False)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model


def extract_embeddings(model, data_dir):
    """
    Extrait les embeddings et les labels pour toutes les images d'un dossier.

    Args:
        model: Modèle PyTorch pour l'extraction d'embeddings.
        data_dir (str): Dossier contenant les sous-dossiers de classes.

    Returns:
        Tuple[np.ndarray, List[str], List[str]]: Embeddings, labels, chemins des images.

    Exemple d'utilisation :
        emb, labels, paths = extract_embeddings(model, 'data/split/test')
    """
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
    """
    Calcule la top-k accuracy pour différents k entre les embeddings de test et de référence.

    Args:
        test_embeddings (np.ndarray): Embeddings des images de test.
        test_labels (List[str]): Labels des images de test.
        ref_embeddings (np.ndarray): Embeddings des images de référence.
        ref_labels (List[str]): Labels des images de référence.
        ks (List[int]): Valeurs de k à tester (ex: [1, 3, 5]).

    Returns:
        Tuple[Dict[str, float], List[str], List[str]]: Dictionnaire des top-k accuracies, labels réels, prédictions top-1.

    Exemple d'utilisation :
        topk_acc, y_true, y_pred = compute_topk_accuracy(...)
    """
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
    """
    Génère et sauvegarde un graphique de top-k accuracy.

    Args:
        topk_acc (Dict[str, float]): Dictionnaire des top-k accuracies.

    Exemple d'utilisation :
        plot_topk({'Top-1': 0.95, 'Top-3': 0.98, 'Top-5': 0.99})
    """
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
    """
    Génère et sauvegarde la matrice de confusion pour les prédictions top-1.

    Args:
        y_true (List[str]): Labels réels.
        y_pred (List[str]): Labels prédits (top-1).

    Exemple d'utilisation :
        plot_confusion(y_true, y_pred)
    """
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
    """
    Point d'entrée du script d'évaluation.
    Charge le modèle, extrait les embeddings, calcule les métriques et génère les graphiques.

    Exemple d'utilisation :
        python evaluate_model.py
    """
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
