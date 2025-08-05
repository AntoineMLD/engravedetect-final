#!/usr/bin/env python3
"""
Script de debug pour comprendre pourquoi le drift ne se déclenche pas.
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


def check_metrics():
    """Vérifie les métriques actuelles."""
    try:
        response = requests.get("http://localhost:8001/metrics")
        if response.status_code == 200:
            metrics = response.text
            print("📊 Métriques actuelles :")

            # Chercher les métriques importantes
            lines = metrics.split("\n")
            for line in lines:
                if any(
                    keyword in line for keyword in ["model_drift_score", "model_predictions_total", "model_embedding_quality"]
                ):
                    print(f"   {line}")
        else:
            print(f"❌ Erreur {response.status_code} lors de la récupération des métriques")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des métriques: {e}")


def check_model_health():
    """Vérifie la santé du modèle."""
    try:
        response = requests.get("http://localhost:8001/model/health")
        if response.status_code == 200:
            health = response.json()
            print("\n🏥 Santé du modèle :")
            print(f"   Status: {health.get('status')}")
            if "model_metrics" in health:
                metrics = health["model_metrics"]
                print(f"   Total prédictions: {metrics.get('total_predictions', 0)}")
                print(f"   Dernière vérification drift: {metrics.get('last_drift_check', 'N/A')}")

        else:
            print(f"❌ Erreur {response.status_code} lors de la vérification de santé")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de santé: {e}")


def make_test_request(token):
    """Fait une requête de test et vérifie les métriques après."""
    try:
        # Trouver une image de test
        image_path = None
        for dir_path in ["data/images", "data/augmented_gravures"]:
            if Path(dir_path).exists():
                images = list(Path(dir_path).glob("*.jpg"))
                if images:
                    image_path = random.choice(images)
                    break

        if not image_path:
            print("❌ Aucune image de test trouvée")
            return False

        print(f"\n🖼️  Test avec {image_path.name}")

        # Faire la requête
        with open(image_path, "rb") as f:
            files = {"file": f}
            headers = {"Authorization": f"Bearer {token}"}

            response = requests.post("http://localhost:8001/match", files=files, headers=headers)

            if response.status_code == 200:
                result = response.json()
                class_name = result["matches"][0]["class_"]
                similarity = result["matches"][0]["similarity"]
                print(f"✅ Prédiction: {class_name} ({similarity:.3f})")

                # Vérifier les métriques après
                time.sleep(1)
                check_metrics()
                return True
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Erreur lors de la requête de test: {e}")
        return False


def main():
    """Fonction principale."""
    print("🔍 Debug de la détection de drift")
    print("=" * 50)

    # Vérifier l'état initial
    print("📊 État initial :")
    check_metrics()
    check_model_health()

    # Obtenir le token
    print("\n🔑 Obtention du token...")
    token = get_token()
    if not token:
        print("❌ Impossible d'obtenir le token. Arrêt.")
        return

    print("✅ Token obtenu")

    # Faire plusieurs requêtes de test
    print("\n🧪 Tests de requêtes :")
    for i in range(1, 6):
        print(f"\n--- Test {i}/5 ---")
        make_test_request(token)
        time.sleep(3)

    # État final
    print("\n📊 État final :")
    check_metrics()
    check_model_health()

    print("\n💡 Si le drift ne s'affiche pas, c'est normal !")
    print("   Le système ne détecte de drift que pour des changements significatifs.")


if __name__ == "__main__":
    main()
