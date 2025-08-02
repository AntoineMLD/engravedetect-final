"""
Script de division du dataset en ensembles d'entraînement, validation et test.

Ce module divise automatiquement le dataset d'images de gravures en trois
ensembles distincts selon des ratios configurables pour l'entraînement
de modèles de deep learning.

Fonctionnalités :
- Division automatique des données par classe
- Respect des ratios train/validation/test
- Préservation de la structure des répertoires
- Gestion des erreurs et validation des chemins
- Reproducibilité avec seed aléatoire

Configuration par défaut :
- Source : ../data/oversampled_gravures
- Cible : ../data/split
- Ratios : 70% train, 15% validation, 15% test
- Seed : 42 pour la reproductibilité

Auteur : Équipe de développement
Version : 1.0.0
"""

import os
import random
import shutil
from pathlib import Path
from typing import Tuple

# Modification des chemins pour pointer vers le dossier data existant
SOURCE_DIR = "../data/oversampled_gravures"
# Modification du chemin cible pour qu'il soit dans le dossier data à la racine
TARGET_DIR = "../data/split"
SPLIT_RATIOS = (0.7, 0.15, 0.15)  # train, val, test
SEED = 42


def split_dataset(source_dir: str, target_dir: str, split_ratios: Tuple[float, float, float], seed: int = 42):
    """
    Divise un dataset d'images en trois ensembles (train, val, test) selon les ratios fournis.

    Args:
        source_dir (str): Chemin du dossier source contenant les sous-dossiers de classes.
        target_dir (str): Chemin du dossier cible où seront créés les sous-dossiers train/val/test.
        split_ratios (Tuple[float, float, float]): Ratios pour train, val, test (doivent totaliser 1.0).
        seed (int, optionnel): Graine aléatoire pour la reproductibilité.

    Cette fonction :
    - Crée la structure de dossiers cible
    - Répartit aléatoirement les images de chaque classe selon les ratios
    - Copie les images dans les bons sous-dossiers
    - Affiche un résumé pour chaque classe

    Exemple d'utilisation :
        split_dataset('../data/oversampled_gravures', '../data/split', (0.7, 0.15, 0.15), seed=42)
    """
    assert sum(split_ratios) == 1.0, "Les ratios doivent totaliser 1.0"

    # Vérifier si le répertoire source existe
    if not os.path.exists(source_dir):
        print(f"Le répertoire source '{source_dir}' n'existe pas.")
        print(f"Veuillez vérifier que le chemin est correct: {os.path.abspath(source_dir)}")
        return

    random.seed(seed)
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(target_dir, split), exist_ok=True)

    # Vérifier si le répertoire source contient des sous-répertoires (classes)
    class_dirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
    if not class_dirs:
        print(f"Le répertoire '{source_dir}' ne contient aucun sous-répertoire de classe.")
        print("Veuillez organiser vos images par classe dans des sous-répertoires.")
        return

    for class_name in class_dirs:
        class_path = os.path.join(source_dir, class_name)

        images = [f for f in os.listdir(class_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not images:
            print(f"Attention: Le répertoire de classe '{class_name}' ne contient aucune image.")
            continue

        random.shuffle(images)

        n_total = len(images)
        n_train = int(split_ratios[0] * n_total)
        n_val = int(split_ratios[1] * n_total)
        n_test = n_total - n_train - n_val

        split_counts = {"train": images[:n_train], "val": images[n_train : n_train + n_val], "test": images[n_train + n_val :]}

        for split_name, split_files in split_counts.items():
            split_dir = os.path.join(target_dir, split_name, class_name)
            os.makedirs(split_dir, exist_ok=True)
            for fname in split_files:
                src_path = os.path.join(class_path, fname)
                dst_path = os.path.join(split_dir, fname)
                shutil.copy2(src_path, dst_path)

        print(f"Classe '{class_name}': {n_train} train, {n_val} val, {n_test} test")

    print(f"\nDossier structuré dans : {target_dir}")


if __name__ == "__main__":
    split_dataset(SOURCE_DIR, TARGET_DIR, SPLIT_RATIOS, seed=SEED)
