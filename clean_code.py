import subprocess
import sys
from pathlib import Path


def run_command(command):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return result.stdout, result.stderr
    except Exception as e:
        print(f"Erreur lors de l'exécution de la commande: {e}")
        return None, None


def clean_code():
    """Nettoie le code en utilisant Black"""
    try:
        # 1. Appliquer Black pour le formatage
        print("Application du formatage avec Black...")
        stdout, stderr = run_command("black .")
        if stderr and "reformatted" not in stderr:
            print("Erreurs Black:", stderr)
        else:
            print("Formatage Black terminé avec succès!")

    except Exception as e:
        print(f"Une erreur s'est produite: {e}")
        sys.exit(1)


if __name__ == "__main__":
    clean_code()
