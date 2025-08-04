#!/usr/bin/env python3
"""
Script de diagnostic des dépendances API IA

Vérifie la compatibilité des versions et identifie les problèmes potentiels.
"""

import sys
import subprocess
from typing import Dict, List, Tuple


def get_installed_packages() -> Dict[str, str]:
    """Récupère la liste des packages installés avec leurs versions"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        packages = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==', 1)
                packages[name.lower()] = version
        return packages
    except subprocess.CalledProcessError:
        return {}


def check_torch_compatibility() -> Tuple[bool, List[str]]:
    """Vérifie la compatibilité PyTorch/TorchVision"""
    issues = []
    
    try:
        import torch
        import torchvision
        
        torch_version = torch.__version__
        torchvision_version = torchvision.__version__
        
        print(f"✅ PyTorch: {torch_version}")
        print(f"✅ TorchVision: {torchvision_version}")
        
        # Test de compatibilité
        try:
            from torchvision import models
            model = models.efficientnet_b0(weights=None)
            print("✅ Test de création de modèle: OK")
        except Exception as e:
            issues.append(f"Erreur création modèle: {e}")
            
        try:
            from torchvision import transforms
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            print("✅ Test de transformations: OK")
        except Exception as e:
            issues.append(f"Erreur transformations: {e}")
            
    except ImportError as e:
        issues.append(f"Import error: {e}")
        return False, issues
    
    return len(issues) == 0, issues


def check_required_packages() -> Dict[str, bool]:
    """Vérifie les packages requis"""
    required = {
        'fastapi': '0.104.1',
        'uvicorn': '0.24.0',
        'torch': '2.2.0',
        'torchvision': '0.17.0',
        'numpy': '1.26.0',
        'pandas': '2.0.0',
        'pillow': '10.0.0',
        'scikit-learn': '1.3.0',
        'prometheus-client': '0.22.1',
        'pyyaml': '6.0.1'
    }
    
    installed = get_installed_packages()
    results = {}
    
    for package, min_version in required.items():
        if package in installed:
            installed_version = installed[package]
            print(f"✅ {package}: {installed_version}")
            results[package] = True
        else:
            print(f"❌ {package}: NON INSTALLÉ")
            results[package] = False
    
    return results


def main():
    """Fonction principale de diagnostic"""
    print("🔍 Diagnostic des dépendances API IA")
    print("=" * 50)
    
    # Vérification des packages requis
    print("\n📦 Packages requis:")
    package_status = check_required_packages()
    
    # Vérification de la compatibilité PyTorch
    print("\n🧠 Compatibilité PyTorch/TorchVision:")
    torch_ok, torch_issues = check_torch_compatibility()
    
    if torch_issues:
        print("❌ Problèmes détectés:")
        for issue in torch_issues:
            print(f"   - {issue}")
    else:
        print("✅ Compatibilité PyTorch/TorchVision: OK")
    
    # Résumé
    print("\n📊 Résumé:")
    all_packages_ok = all(package_status.values())
    if all_packages_ok and torch_ok:
        print("✅ Toutes les dépendances sont correctement installées")
        return 0
    else:
        print("❌ Problèmes détectés dans les dépendances")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 