# Chaîne de Livraison Continue du Modèle d'IA (MLOps)

## 1. Vue d'ensemble

Ce document décrit la chaîne de livraison continue (CI/CD) mise en place pour le modèle d'IA EngraveDetect, suivant les principes MLOps.

## 2. Déclencheurs

La chaîne est déclenchée automatiquement dans les cas suivants :
- Push sur la branche `main`
- Pull Request vers la branche `main`
- Push sur la branche `ci/cd`

## 3. Étapes de la Chaîne

### 3.1 Validation du Modèle

#### 3.1.1 Tests d'Évaluation
- Tests de performance du modèle
  - Précision Top-k (Top-1, Top-3, Top-5)
  - Matrice de confusion
  - Similarité cosinus
- Tests de robustesse
  - Cas limites
  - Données de grande taille
  - Cohérence des résultats

#### 3.1.2 Tests de Performance
- Tests du modèle d'IA
  - Temps de prédiction
  - Utilisation mémoire
  - Gestion GPU/CPU
- Tests de l'API
  - Temps de réponse
  - Débit
- Tests de la base de données
  - Temps de requête
  - Utilisation mémoire

### 3.2 Tests Automatisés (CI)

#### 3.2.1 Configuration de l'Environnement
- Checkout du code
- Configuration de Python 3.10
- Installation des dépendances
  - Dépendances principales (requirements.txt)
  - Dépendances de test (pytest, pytest-asyncio, pytest-cov)
  - Installation du package en mode développement (-e .)
- Configuration du PYTHONPATH
  - Ajout du dossier src au PYTHONPATH
  - Ajout du dossier racine au PYTHONPATH

#### 3.2.2 Tests de Code
- Tests unitaires avec pytest
  - Exécution de tous les tests dans le dossier tests/
  - Mode verbeux pour plus de détails
  - Configuration de la clé secrète pour les tests
- Couverture de code
  - Génération du rapport XML
  - Génération du rapport terminal

### 3.3 Packaging

#### 3.3.1 Configuration Docker
- Image de base : Python 3.10-slim
- Environnement Python
  - PYTHONUNBUFFERED=1
  - PYTHONDONTWRITEBYTECODE=1
  - PYTHONPATH=/app
- Dépendances système
  - build-essential
  - libgl1-mesa-glx
  - curl, gnupg, libmagic1
- Sécurité
  - Utilisateur non-root (appuser)
  - Permissions minimales

#### 3.3.2 Build Docker
- Construction de l'image
  - Tag : api_bdd
  - Copie des dépendances
  - Copie du code source
  - Copie des poids du modèle

### 3.4 Déploiement (CD)

#### 3.4.1 Build
- Construction de l'image Docker pour test local
- Pas de déploiement configuré actuellement

## 4. Configuration

### 4.1 Fichiers de Configuration
- `.github/workflows/ci.yml`
- `.github/workflows/cd.yml`
- `pytest.ini`
- `.flake8`
- `Dockerfile.api_ia`

### 4.2 Variables d'Environnement
```env
SECRET_KEY=test-secret-key-for-testing-only
DATABASE_URL=postgresql://postgres:******@localhost:5432/glass_db
ADMIN_EMAIL=<admin-email>
ADMIN_PASSWORD=<admin-password>
database_url=sqlite:///./test.db
```

## 5. Monitoring

### 5.1 Métriques
- Couverture de code
- Performance du modèle
- Temps de réponse API
- Utilisation mémoire

## 6. Documentation

### 6.1 Liens vers la Documentation
- [Documentation API](C9_API_IA.md)
- [Documentation Intégration](C10_Integration_API_IA.md)
- [Documentation Base de Données](C4_Base_Donnees_RGPD.md)

## 7. Procédures d'Installation et de Configuration

### 7.1 Prérequis
- Git 2.x ou supérieur
- Docker 20.x ou supérieur
- Python 3.10
- Compte GitHub avec accès au repository

### 7.2 Installation
1. Cloner le repository :
   ```bash
   git clone 
   cd engravedetect
   ```

2. Installer les dépendances Python :
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou `venv\Scripts\activate` sur Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   # Éditer .env avec vos configurations
   ```

### 7.3 Configuration
1. Configurer GitHub Actions :
   - Aller dans Settings > Secrets and variables > Actions
   - Ajouter les secrets nécessaires :
     - `SECRET_KEY` pour les tests
     - `DATABASE_URL` pour la connexion PostgreSQL
     - `ADMIN_EMAIL`, `ADMIN_PASSWORD`

2. Configurer les tests :
   - Vérifier que `pytest.ini` est présent
   - Vérifier que `.flake8` est présent
   - Vérifier que les chemins dans les fichiers de configuration sont corrects

### 7.4 Test de la Chaîne
1. Tests locaux :
   ```bash
   # Tests unitaires
   pytest tests/
   
   # Tests de performance
   pytest tests/test_performance.py
   
   # Linting
   flake8 src/
   ```

2. Test de la chaîne CI/CD :
   - Créer une branche de test
   - Faire un push pour déclencher la CI
   - Vérifier que tous les jobs passent

3. Dépannage courant :
   - Si les tests échouent : vérifier les logs dans GitHub Actions
   - Si le build Docker échoue : vérifier les logs de build
   - Si les tests de performance échouent : vérifier la disponibilité du modèle 