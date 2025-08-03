#!/usr/bin/env python3
"""
Script d'installation et de configuration de Playwright
"""
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()


def run_command(command: str, description: str) -> bool:
    """
    Exécute une commande et affiche le résultat

    Args:
        command: Commande à exécuter
        description: Description de la commande

    Returns:
        True si la commande réussit, False sinon
    """
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        if result.stdout:
            print(f"   Sortie: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Échec")
        print(f"   Erreur: {e.stderr.strip()}")
        return False


def check_python_version() -> bool:
    """
    Vérifie que la version de Python est compatible

    Returns:
        True si la version est compatible
    """
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ est requis")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True


def install_playwright() -> bool:
    """
    Installe Playwright et ses dépendances

    Returns:
        True si l'installation réussit
    """
    # Installation via pip
    if not run_command("pip install playwright pytest-playwright", "Installation de Playwright via pip"):
        return False

    # Installation des navigateurs
    if not run_command("playwright install", "Installation des navigateurs Playwright"):
        return False

    # Installation des navigateurs spécifiques
    browsers = ["chromium", "firefox", "webkit"]
    for browser in browsers:
        if not run_command(f"playwright install {browser}", f"Installation du navigateur {browser}"):
            return False

    return True


def create_test_data_directory() -> bool:
    """
    Crée le répertoire de données de test

    Returns:
        True si la création réussit
    """
    test_data_dir = Path("tests/test_data")
    try:
        test_data_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Répertoire de test créé: {test_data_dir}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du répertoire: {e}")
        return False


def create_sample_test_image() -> bool:
    """
    Crée une image de test simple pour les tests Playwright

    Returns:
        True si la création réussit
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Création d'une image de test simple
        img = Image.new("RGB", (100, 100), color="white")
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), "Test", fill="black")

        test_data_dir = Path("tests/test_data")
        test_data_dir.mkdir(parents=True, exist_ok=True)

        img_path = test_data_dir / "test_image.jpg"
        img.save(img_path, "JPEG")

        print(f"✅ Image de test créée: {img_path}")
        return True
    except ImportError:
        print("⚠️  PIL/Pillow non installé - image de test non créée")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'image de test: {e}")
        return False


def verify_installation() -> bool:
    """
    Vérifie que l'installation de Playwright fonctionne

    Returns:
        True si la vérification réussit
    """
    try:
        import playwright
        from playwright.sync_api import sync_playwright

        print("🔄 Test de Playwright...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://example.com")
            title = page.title()
            browser.close()

            if "Example Domain" in title:
                print("✅ Test de Playwright réussi")
                return True
            else:
                print("❌ Test de Playwright échoué")
                return False

    except Exception as e:
        print(f"❌ Erreur lors du test de Playwright: {e}")
        return False


def main():
    """
    Fonction principale du script d'installation
    """
    print("🚀 Installation et configuration de Playwright")
    print("=" * 50)

    # Vérification de la version Python
    if not check_python_version():
        sys.exit(1)

    # Installation de Playwright
    if not install_playwright():
        print("❌ Échec de l'installation de Playwright")
        sys.exit(1)

    # Création du répertoire de test
    if not create_test_data_directory():
        print("❌ Échec de la création du répertoire de test")
        sys.exit(1)

    # Création d'une image de test
    create_sample_test_image()

    # Vérification de l'installation
    if not verify_installation():
        print("❌ Échec de la vérification de l'installation")
        sys.exit(1)

    print("\n🎉 Installation de Playwright terminée avec succès!")
    print("\n📋 Prochaines étapes:")
    print("1. Configurer les variables d'environnement:")
    print("   cp env.example .env")
    print("   # Éditer .env avec vos identifiants")
    print("2. Exécuter les tests Playwright: python scripts/run_playwright_tests.py")
    print("3. Exécuter tous les tests: pytest tests/ -v")
    print("\n📚 Documentation:")
    print("- Tests Playwright: tests/test_playwright_e2e.py")
    print("- Configuration: playwright.config.py")
    print("- Variables d'environnement: .env")


if __name__ == "__main__":
    main()
