# Formatage du Code - EngraveDetect

Ce document décrit les règles et outils de formatage utilisés dans le projet EngraveDetect pour maintenir une cohérence de style de code.

## Outils Utilisés

### Black
- **Objectif** : Formatage automatique du code Python
- **Configuration** : `pyproject.toml`
- **Longueur de ligne** : 127 caractères
- **Version Python cible** : 3.10

### isort
- **Objectif** : Tri automatique des imports Python
- **Configuration** : `pyproject.toml`
- **Profil** : Compatible avec Black
- **Longueur de ligne** : 127 caractères

### flake8
- **Objectif** : Vérification de la qualité du code
- **Configuration** : `.flake8`
- **Longueur de ligne** : 100 caractères
- **Règles ignorées** : E203, W503, E501, F401

## Utilisation

### Formatage Automatique

Pour formater automatiquement tout le code du projet :

```bash
# Appliquer les corrections
python scripts/format_code.py

# Ou avec l'option explicite
python scripts/format_code.py --fix
```

### Vérification Seule

Pour vérifier le formatage sans appliquer de changements :

```bash
python scripts/format_code.py --check
```

### Commandes Manuelles

Si vous préférez utiliser les outils directement :

```bash
# Formatage avec Black
black .

# Tri des imports avec isort
isort .

# Vérification avec flake8
flake8 .
```

## Règles de Formatage

### Imports

1. **Ordre des imports** :
   - Imports de la bibliothèque standard Python
   - Ligne vide
   - Imports de bibliothèques tierces
   - Ligne vide
   - Imports locaux du projet

2. **Exemple** :
   ```python
   import os
   import sys
   from typing import List, Optional
   
   import numpy as np
   import torch
   from fastapi import FastAPI
   
   from src.api.core.config import settings
   from src.models.efficientnet_triplet import EfficientNetEmbedding
   ```

### Style de Code

1. **Longueur de ligne** : Maximum 127 caractères
2. **Guillemets** : Double guillemets pour les chaînes
3. **Espaces** : 4 espaces pour l'indentation
4. **Virgules finales** : Oui pour les structures multi-lignes

### Documentation

1. **Docstrings** : Format Google ou NumPy
2. **Commentaires** : En français, explicatifs
3. **Noms de variables** : En français, descriptifs

## Intégration Continue

Le formatage est vérifié automatiquement dans les pipelines CI/CD :

- Vérification avec `black --check --diff`
- Vérification avec `isort --check-only --diff`
- Vérification avec `flake8`

## Résolution des Problèmes

### Erreurs Courantes

1. **Imports mal triés** :
   ```bash
   isort .
   ```

2. **Formatage incorrect** :
   ```bash
   black .
   ```

3. **Violations de style** :
   ```bash
   flake8 .
   ```

### Pré-commit Hooks

Pour éviter les problèmes avant les commits, vous pouvez installer des hooks pre-commit :

```bash
# Installation (optionnel)
pip install pre-commit
pre-commit install
```

## Configuration

### pyproject.toml

```toml
[tool.black]
line-length = 127
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 127
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip = ["venv", ".venv", "engravedetect-env"]
```

### .flake8

```ini
[flake8]
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    engravedetect-env,
    backups,
    .venv
max-line-length = 100
ignore = E203, W503, E501, F401
per-file-ignores =
    __init__.py:F401
max-complexity = 10
```

## Bonnes Pratiques

1. **Formatez régulièrement** : Utilisez le script de formatage avant chaque commit
2. **Vérifiez les erreurs** : Corrigez les violations de style détectées
3. **Documentez les exceptions** : Si vous devez ignorer une règle, documentez pourquoi
4. **Maintenez la cohérence** : Respectez le style établi dans le projet

## Support

Pour toute question sur le formatage du code :

1. Consultez la documentation des outils
2. Vérifiez la configuration dans `pyproject.toml` et `.flake8`
3. Utilisez le script de formatage automatique
4. Contactez l'équipe de développement si nécessaire 