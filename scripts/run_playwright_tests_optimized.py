#!/usr/bin/env python3
"""
Script optimisé pour exécuter les tests Playwright

Ce script optimise l'exécution des tests en :
- Utilisant des workers parallèles
- Désactivant les tests lents en CI
- Réduisant les timeouts
- Filtrant les tests problématiques

Usage :
    python scripts/run_playwright_tests_optimized.py [options]

Options :
    --fast    : Mode rapide (tests essentiels seulement)
    --ci      : Mode CI (désactive les tests lents)
    --debug   : Mode debug avec plus de logs
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Exécute une commande et affiche le résultat."""
    print(f" {description}...")
    print(f"Commande: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f" {description} terminé avec succès")
        if result.stdout:
            print("Sortie:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f" Erreur lors de {description}:")
        print(f"Code de sortie: {e.returncode}")
        if e.stdout:
            print("Sortie standard:")
            print(e.stdout)
        if e.stderr:
            print("Sortie d'erreur:")
            print(e.stderr)
        return False


def main():
    """Fonction principale du script."""
    parser = argparse.ArgumentParser(description="Exécuter les tests Playwright optimisés")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Mode rapide (tests essentiels seulement)",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Mode CI (désactive les tests lents)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Mode debug avec plus de logs",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Nombre de workers parallèles (défaut: 2)",
    )

    args = parser.parse_args()

    print(" Démarrage des tests Playwright optimisés...")

    # Obtenir le répertoire racine du projet
    project_root = Path(__file__).parent.parent
    print(f"Répertoire du projet: {project_root}")

    # Configuration de base
    test_file = "tests/test_playwright_e2e.py"
    output_dir = "test-results"

    # Créer le répertoire de sortie
    os.makedirs(output_dir, exist_ok=True)

    # Construction de la commande pytest
    cmd_parts = [
        "python",
        "-m",
        "pytest",
        test_file,
        "-v",
        "--disable-warnings",
        f"--junitxml={output_dir}/results.xml",
        f"-n={args.workers}",  # Workers parallèles
        "--dist=worksteal",  # Distribution des tests
        "--timeout=30",  # Timeout réduit
        "--timeout-method=thread",  # Méthode de timeout
    ]

    # Options selon le mode
    if args.fast:
        print(" Mode rapide activé")
        cmd_parts.extend(
            [
                "-m",
                "not slow",  # Exclure les tests lents
                "--tb=short",  # Traceback court
            ]
        )

    if args.ci:
        print(" Mode CI activé")
        cmd_parts.extend(
            [
                "-m",
                "not slow",  # Exclure les tests lents
                "--tb=short",  # Traceback court
                "--strict-markers",  # Marqueurs stricts
            ]
        )
        # Définir les variables d'environnement pour CI
        os.environ["CI"] = "true"

    if args.debug:
        print(" Mode debug activé")
        cmd_parts.extend(
            [
                "-s",  # Sortie non capturée
                "--tb=long",  # Traceback détaillé
            ]
        )

    # Ajouter des options pour optimiser les performances
    cmd_parts.extend(
        [
            "--maxfail=5",  # Arrêter après 5 échecs
            "--durations=10",  # Afficher les 10 tests les plus lents
            "--strict-config",  # Configuration stricte
        ]
    )

    # Construire la commande finale
    command = " ".join(cmd_parts)

    print(f"Configuration:")
    print(f"- Mode rapide: {args.fast}")
    print(f"- Mode CI: {args.ci}")
    print(f"- Mode debug: {args.debug}")
    print(f"- Workers: {args.workers}")
    print(f"- Timeout: 30s")

    # Exécuter les tests
    success = run_command(command, "Exécution des tests Playwright")

    # Résultat final
    if success:
        print("\n Tests terminés avec succès!")
        return 0
    else:
        print("\n Certains tests ont échoué")
        print(" Conseils pour résoudre les problèmes:")
        print("   - Vérifiez que le site https://engravedetect.fr est accessible")
        print("   - Vérifiez les variables d'environnement ADMIN_USERNAME et ADMIN_PASSWORD")
        print("   - Utilisez --debug pour plus de détails")
        print("   - Utilisez --fast pour les tests essentiels seulement")
        return 1


if __name__ == "__main__":
    sys.exit(main())
