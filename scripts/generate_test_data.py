#!/usr/bin/env python3
"""
Script pour générer des données de test pour les métriques du modèle IA.
"""

import requests
import time
import json
from pathlib import Path

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

def find_test_image():
    """Trouve une image de test dans le projet."""
    # Chercher dans les dossiers d'images
    image_dirs = [
        "data/images",
        "data/augmented_gravures",
        "tests/test_data"
    ]
    
    for dir_path in image_dirs:
        if Path(dir_path).exists():
            for ext in ["*.jpg", "*.png", "*.jpeg"]:
                images = list(Path(dir_path).glob(ext))
                if images:
                    return str(images[0])
    
    return None

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
                print(f"✅ Prédiction réussie: {result['matches'][0]['class_']} ({result['matches'][0]['similarity']:.3f})")
                return True
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors de la requête: {e}")
        return False

def main():
    """Fonction principale."""
    print("🚀 Génération de données de test pour les métriques du modèle IA")
    print("=" * 60)
    
    # Obtenir le token
    print("🔑 Obtention du token d'authentification...")
    token = get_token()
    if not token:
        print("❌ Impossible d'obtenir le token. Arrêt.")
        return
    
    print("✅ Token obtenu avec succès")
    
    # Trouver une image de test
    print("🖼️  Recherche d'une image de test...")
    image_path = find_test_image()
    if not image_path:
        print("❌ Aucune image de test trouvée. Arrêt.")
        return
    
    print(f"✅ Image trouvée: {image_path}")
    
    # Faire plusieurs requêtes
    print("\n📊 Génération de données de test...")
    success_count = 0
    
    for i in range(1, 11):
        print(f"\n📈 Requête {i}/10...")
        if make_prediction_request(token, image_path):
            success_count += 1
        
        # Pause entre les requêtes
        if i < 10:
            time.sleep(1)
    
    print(f"\n🎉 Terminé ! {success_count}/10 requêtes réussies")
    print("\n📋 Vérifiez maintenant votre dashboard Grafana pour voir les métriques !")
    print("   URL: http://localhost:3001")

if __name__ == "__main__":
    main() 