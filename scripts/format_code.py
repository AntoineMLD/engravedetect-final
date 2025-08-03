#!/usr/bin/env python3
"""
Script de formatage automatique du code

Ce script applique automatiquement le formatage avec black et isort
pour maintenir la cohérence du style de code dans le projet.

Fonctionnalités :
- Formatage avec black (style de code)
- Tri des imports avec isort
- Vérification des erreurs de formatage
- Application automatique des corrections

Usage :
    python scripts/format_code.py [--check] [--fix]

Options :
    --check : Vérifier seulement sans appliquer les changements
    --fix   : Appliquer automatiquement les corrections (défaut)
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Exécute une commande et affiche le résultat."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        print(f"✅ {description} terminé avec succès")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}:")
        print(f"Commande: {command}")
        print(f"Sortie d'erreur: {e.stderr}")
        return False


def main():
    """Fonction principale du script."""
    parser = argparse.ArgumentParser(description="Formater le code avec black et isort")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Vérifier seulement sans appliquer les changements",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Appliquer automatiquement les corrections (défaut)",
    )
    
    args = parser.parse_args()
    
    # Déterminer le mode d'opération
    check_mode = args.check
    fix_mode = args.fix or not check_mode
    
    print("🚀 Démarrage du formatage du code...")
    print(f"Mode: {'Vérification' if check_mode else 'Correction'}")
    
    # Obtenir le répertoire racine du projet
    project_root = Path(__file__).parent.parent
    print(f"Répertoire du projet: {project_root}")
    
    success = True
    
    # Formater avec black
    black_cmd = f"black {project_root}"
    if check_mode:
        black_cmd += " --check --diff"
    
    if not run_command(black_cmd, "Formatage avec black"):
        success = False
    
    # Trier les imports avec isort
    isort_cmd = f"isort {project_root}"
    if check_mode:
        isort_cmd += " --check-only --diff"
    
    if not run_command(isort_cmd, "Tri des imports avec isort"):
        success = False
    
    # Résultat final
    if success:
        print("\n🎉 Formatage terminé avec succès!")
        if check_mode:
            print("✅ Tous les fichiers sont correctement formatés")
        else:
            print("✅ Tous les fichiers ont été formatés")
        return 0
    else:
        print("\n❌ Erreurs détectées lors du formatage")
        if check_mode:
            print("💡 Utilisez --fix pour corriger automatiquement les problèmes")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 