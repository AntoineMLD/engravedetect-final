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
