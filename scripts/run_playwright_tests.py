#!/usr/bin/env python3
"""
Script pour exécuter les tests Playwright
"""
import subprocess
import sys
import argparse
import os
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
    print(f"   Commande: {command}")

    try:
        result = subprocess.run(command, shell=True, check=True, text=True)
        print(f"✅ {description} - Succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Échec")
        print(f"   Code de sortie: {e.returncode}")
        return False


def check_playwright_installation() -> bool:
    """
    Vérifie que Playwright est installé

    Returns:
        True si Playwright est installé
    """
    try:
        import playwright

        print("✅ Playwright est installé")
        return True
    except ImportError:
        print("❌ Playwright n'est pas installé")
        print("   Exécutez: pip install -r requirements-dev.txt")
        return False


def check_environment_variables() -> bool:
    """
    Vérifie que les variables d'environnement nécessaires sont définies

    Returns:
        True si les variables sont définies
    """
    required_vars = ["ADMIN_USERNAME", "ADMIN_PASSWORD"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("   Créez un fichier .env basé sur env.example")
        print("   Exemple:")
        print("   ADMIN_USERNAME=***")
        print("   ADMIN_PASSWORD=****")
        return False

    print("✅ Variables d'environnement configurées")
    return True


def run_tests(test_type: str, headed: bool = False, verbose: bool = True) -> bool:
    """
    Exécute les tests Playwright

    Args:
        test_type: Type de test à exécuter
        headed: Mode avec interface graphique
        verbose: Mode verbeux

    Returns:
        True si les tests réussissent
    """
    # Construction de la commande
    cmd_parts = ["python", "-m", "pytest"]

    if test_type == "all":
        cmd_parts.append("tests/test_playwright_e2e.py")
    elif test_type == "auth":
        cmd_parts.append("tests/test_playwright_e2e.py::TestAuthentification")
    elif test_type == "ui":
        cmd_parts.append("tests/test_playwright_e2e.py::TestInterfaceUtilisateur")
    elif test_type == "performance":
        cmd_parts.append("tests/test_playwright_e2e.py::TestPerformanceInterface")
    elif test_type == "accessibility":
        cmd_parts.append("tests/test_playwright_e2e.py::TestAccessibilite")
    else:
        print(f"❌ Type de test inconnu: {test_type}")
        return False

    if headed:
        cmd_parts.append("--headed")

    if verbose:
        cmd_parts.append("-v")

    cmd_parts.append("--tb=short")

    command = " ".join(cmd_parts)

    return run_command(command, f"Exécution des tests {test_type}")


def run_specific_test(test_name: str, headed: bool = False) -> bool:
    """
    Exécute un test spécifique

    Args:
        test_name: Nom du test à exécuter
        headed: Mode avec interface graphique

    Returns:
        True si le test réussit
    """
    cmd_parts = ["python", "-m", "pytest", f"tests/test_playwright_e2e.py::{test_name}", "-v"]

    if headed:
        cmd_parts.append("--headed")

    command = " ".join(cmd_parts)

    return run_command(command, f"Exécution du test {test_name}")


def list_available_tests() -> None:
    """
    Liste tous les tests Playwright disponibles
    """
    print("📋 Tests Playwright disponibles:")
    print()

    test_file = Path("tests/test_playwright_e2e.py")
    if not test_file.exists():
        print("❌ Fichier de tests Playwright non trouvé")
        return

    try:
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Extraction des noms de classes et méthodes de test
        lines = content.split("\n")
        current_class = None

        for line in lines:
            line = line.strip()

            # Détection des classes de test
            if line.startswith("class Test") and line.endswith(":"):
                current_class = line.split("class ")[1].split("(")[0]
                print(f"📁 {current_class}")

            # Détection des méthodes de test
            elif line.startswith("def test_") and line.endswith(":"):
                if current_class:
                    test_name = line.split("def ")[1].split("(")[0]
                    print(f"   └── {current_class}.{test_name}")
                else:
                    test_name = line.split("def ")[1].split("(")[0]
                    print(f"   └── {test_name}")

    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier de tests: {e}")


def main():
    """
    Fonction principale
    """
    parser = argparse.ArgumentParser(description="Script d'exécution des tests Playwright")
    parser.add_argument(
        "--type", choices=["all", "auth", "ui", "performance", "accessibility"], default="all", help="Type de tests à exécuter"
    )
    parser.add_argument("--test", help="Nom spécifique d'un test à exécuter")
    parser.add_argument("--headed", action="store_true", help="Exécuter en mode visible (avec interface graphique)")
    parser.add_argument("--list", action="store_true", help="Lister tous les tests disponibles")
    parser.add_argument("--quiet", action="store_true", help="Mode silencieux")

    args = parser.parse_args()

    print("🧪 Tests Playwright - EngraveDetect")
    print("=" * 40)

    # Vérification de l'installation
    if not check_playwright_installation():
        sys.exit(1)

    # Vérification des variables d'environnement
    if not check_environment_variables():
        sys.exit(1)

    # Liste des tests
    if args.list:
        list_available_tests()
        return

    # Exécution d'un test spécifique
    if args.test:
        success = run_specific_test(args.test, args.headed)
        sys.exit(0 if success else 1)

    # Exécution des tests par type
    success = run_tests(args.type, args.headed, not args.quiet)

    if success:
        print("\n🎉 Tous les tests ont réussi!")
    else:
        print("\n❌ Certains tests ont échoué")
        print("\n💡 Conseils:")
        print("   - Vérifiez que l'application est lancée sur http://localhost:8000")
        print("   - Utilisez --headed pour voir le navigateur")
        print("   - Utilisez --list pour voir tous les tests disponibles")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
