#!/usr/bin/env python3
"""
Script pour tester la détection de drift avec beaucoup de requêtes et images diverses.
"""

import json
import random
import time
from pathlib import Path

import requests


def get_token():
    """Obtient un token d'authentification."""
    try:
        response = requests.post("http://localhost:8001/token", data={"username": "admin", "password": "adminpass123"})
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Erreur lors de l'obtention du token: {e}")
        return None


def find_diverse_images():
    """Trouve des images très différentes pour maximiser le drift."""
    image_dirs = ["data/augmented_gravures", "data/oversampled_gravures", "data/images"]

    all_images = []
    for dir_path in image_dirs:
        if Path(dir_path).exists():
            for ext in ["*.jpg", "*.png", "*.jpeg"]:
                images = list(Path(dir_path).glob(ext))
                all_images.extend(images)

    # Prendre plus d'images pour maximiser les chances de drift
    if len(all_images) > 30:
        return random.sample(all_images, 30)
    return all_images


def make_prediction_request(token, image_path):
    """Fait une requête de prédiction."""
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            headers = {"Authorization": f"Bearer {token}"}

            response = requests.post("http://localhost:8001/match", files=files, headers=headers)

            if response.status_code == 200:
                result = response.json()
                class_name = result["matches"][0]["class_"]
                similarity = result["matches"][0]["similarity"]
                print(f" {Path(image_path).name} → {class_name} ({similarity:.3f})")
                return True
            elif response.status_code == 429:
                print(f"⏳ Rate limit atteint, pause de 60s...")
                time.sleep(60)
                return False
            else:
                print(f" Erreur {response.status_code}: {response.text}")
                return False

    except Exception as e:
        print(f" Erreur lors de la requête: {e}")
        return False


def main():
    """Fonction principale."""
    print(" Test de détection de drift avec données très diverses")
    print("=" * 60)

    # Obtenir le token
    print(" Obtention du token d'authentification...")
    token = get_token()
    if not token:
        print(" Impossible d'obtenir le token. Arrêt.")
        return

    print(" Token obtenu avec succès")

    # Trouver des images très diverses
    print("  Recherche d'images très diverses...")
    images = find_diverse_images()
    if not images:
        print(" Aucune image trouvée. Arrêt.")
        return

    print(f" {len(images)} images trouvées pour le test")

    # Faire beaucoup de requêtes avec des images différentes
    print("\n Test de drift avec images très diverses...")
    print(" Avec 10% de probabilité de détection, il faut ~30-50 requêtes")
    success_count = 0

    # Faire plusieurs cycles pour maximiser les chances
    for cycle in range(1, 4):
        print(f"\n Cycle {cycle}/3")

        for i, image_path in enumerate(images, 1):
            print(f" Requête {i}/{len(images)} avec {Path(image_path).name}...")
            if make_prediction_request(token, image_path):
                success_count += 1

            # Pause courte entre les requêtes
            if i < len(images):
                print("⏳ Pause de 2s...")
                time.sleep(2)

        # Pause entre les cycles
        if cycle < 3:
            print(f"⏳ Pause de 30s entre les cycles...")
            time.sleep(30)

    print(f"\n Terminé ! {success_count} requêtes réussies sur {len(images) * 3} total")
    print("\n Vérifiez maintenant votre dashboard Grafana pour voir le drift !")
    print("   URL: http://localhost:3001")
    print("\n Avec 30% de probabilité et 90 requêtes, vous devriez voir du drift.")


if __name__ == "__main__":
    main()
