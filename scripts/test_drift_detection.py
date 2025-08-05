#!/usr/bin/env python3
"""
Script pour tester la détection de drift avec différentes images.
"""

import requests
import time
import json
from pathlib import Path
import random

def get_token():
    """Obtient un token d'authentification."""
    try:
        response = requests.post(
            "http://localhost:8001/token",
            data={"username": "admin", "password": "adminpass123"}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Erreur lors de l'obtention du token: {e}")
        return None

def find_diverse_images():
    """Trouve des images différentes pour tester le drift."""
    image_dirs = [
        "data/images",
        "data/augmented_gravures",
        "data/oversampled_gravures"
    ]
    
    all_images = []
    for dir_path in image_dirs:
        if Path(dir_path).exists():
            for ext in ["*.jpg", "*.png", "*.jpeg"]:
                images = list(Path(dir_path).glob(ext))
                all_images.extend(images)
    
    # Prendre des images aléatoires pour maximiser la diversité
    if len(all_images) > 10:
        return random.sample(all_images, 10)
    return all_images

def make_prediction_request(token, image_path):
    """Fait une requête de prédiction."""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                "http://localhost:8001/match",
                files=files,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                class_name = result['matches'][0]['class_']
                similarity = result['matches'][0]['similarity']
                print(f"✅ {Path(image_path).name} → {class_name} ({similarity:.3f})")
                return True
            elif response.status_code == 429:
                print(f"⏳ Rate limit atteint, pause de 60s...")
                time.sleep(60)
                return False
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors de la requête: {e}")
        return False

def main():
    """Fonction principale."""
    print("🚀 Test de détection de drift avec données diverses")
    print("=" * 60)
    
    # Obtenir le token
    print("🔑 Obtention du token d'authentification...")
    token = get_token()
    if not token:
        print("❌ Impossible d'obtenir le token. Arrêt.")
        return
    
    print("✅ Token obtenu avec succès")
    
    # Trouver des images diverses
    print("🖼️  Recherche d'images diverses...")
    images = find_diverse_images()
    if not images:
        print("❌ Aucune image trouvée. Arrêt.")
        return
    
    print(f"✅ {len(images)} images trouvées pour le test")
    
    # Faire des requêtes avec des images différentes
    print("\n📊 Test de drift avec images diverses...")
    success_count = 0
    
    for i, image_path in enumerate(images, 1):
        print(f"\n📈 Requête {i}/{len(images)} avec {Path(image_path).name}...")
        if make_prediction_request(token, image_path):
            success_count += 1
        
        # Pause entre les requêtes pour éviter le rate limit
        if i < len(images):
            print("⏳ Pause de 12s...")
            time.sleep(12)
    
    print(f"\n🎉 Terminé ! {success_count}/{len(images)} requêtes réussies")
    print("\n📋 Vérifiez maintenant votre dashboard Grafana pour voir le drift !")
    print("   URL: http://localhost:3001")
    print("\n💡 Le drift devrait être visible si les embeddings sont suffisamment différents.")

if __name__ == "__main__":
    main() 