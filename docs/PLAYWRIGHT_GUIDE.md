# Guide Playwright pour EngraveDetect

Ce guide explique comment utiliser Playwright pour les tests end-to-end dans le projet EngraveDetect.

---

##  Qu'est-ce que Playwright ?

Playwright est un framework de test automatisé pour les navigateurs web. Il permet de :
- Tester l'interface utilisateur de bout en bout
- Simuler les interactions utilisateur (clic, saisie, navigation)
- Tester sur différents navigateurs (Chrome, Firefox, Safari)
- Vérifier le comportement responsive
- Tester l'accessibilité

---

##  Installation rapide

### 1. Installation automatique
```bash
# Depuis la racine du projet
python scripts/setup_playwright.py
```

### 2. Configuration des variables d'environnement
```bash
# Copier le fichier d'exemple
cp env.example .env

# Éditer le fichier .env avec vos identifiants
# ADMIN_USERNAME=********
# ADMIN_PASSWORD=*****
```

### 3. Installation manuelle
```bash
# Installation des dépendances
pip install -r requirements-dev.txt

# Installation des navigateurs
playwright install
```

---

##  Structure des tests

### Organisation des tests
```
tests/
├── test_playwright_e2e.py    # Tests Playwright principaux
├── test_data/                # Données de test
│   └── test_image.jpg        # Image de test
└── conftest.py              # Configuration pytest
```

### Marqueurs de test
- `@pytest.mark.playwright` : Tests utilisant Playwright
- `@pytest.mark.e2e` : Tests end-to-end
- `@pytest.mark.slow` : Tests lents (performance)
- `@pytest.mark.integration` : Tests d'intégration

---

##  Exécution des tests

### Tests de base
```bash
# Tous les tests Playwright
pytest tests/test_playwright_e2e.py -v

# Tests avec marqueurs spécifiques
pytest -m "playwright" -v
pytest -m "e2e" -v
pytest -m "not slow" -v
```

### Tests dans Docker
```bash
# Tests dans le conteneur
docker compose exec api_ia pytest tests/test_playwright_e2e.py -v

# Tests avec interface graphique (débug)
docker compose exec api_ia pytest tests/test_playwright_e2e.py --headed
```

---

##  Exemples de tests

### Test de connexion
```python
import os
from playwright.sync_api import Page, expect

@pytest.mark.playwright
def test_connexion_utilisateur(page: Page):
    """Test de connexion avec les identifiants admin"""
    page.goto("https://engravedetect.fr")
    
    # Remplissage du formulaire de connexion
    admin_username = os.getenv("ADMIN_USERNAME", "****")
    admin_password = os.getenv("ADMIN_PASSWORD", "*****")
    page.fill('input[placeholder*="nom d\'utilisateur"]', admin_username)
    page.fill('input[placeholder*="mot de passe"]', admin_password)
    page.click('button:has-text("Se connecter")')
    
    # Vérification de la connexion
    expect(page.locator("text= Déconnexion")).to_be_visible()
```

### Test d'upload d'image
```python
@pytest.mark.playwright
def test_upload_image(page: Page):
    """Test d'upload d'image pour l'analyse IA"""
    page.goto("https://engravedetect.fr")
    
    # Upload d'une image de test
    with page.expect_file_chooser() as fc_info:
        page.click('input[type="file"]')
    file_chooser = fc_info.value
    file_chooser.set_files("tests/test_data/test_image.jpg")
    
    # Vérification du résultat
    expect(page.locator("text=Résultats de l'analyse")).to_be_visible()
```

---

##  Configuration

### Variables d'environnement requises
```bash
# Identifiants de test
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password

# URL de test
TEST_URL=https://engravedetect.fr

# Configuration Playwright
PLAYWRIGHT_BROWSER=chromium
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
```

### Configuration pytest
```ini
# pytest.ini
[tool:pytest]
markers =
    playwright: marks tests as playwright tests
    e2e: marks tests as end-to-end tests
    slow: marks tests as slow
    integration: marks tests as integration tests
```

---

##  Rapports et résultats

### Génération de rapports
```bash
# Rapport XML pour CI/CD
pytest tests/test_playwright_e2e.py --junitxml=test-results/results.xml

# Rapport HTML
pytest tests/test_playwright_e2e.py --html=test-results/report.html
```

### Artefacts de test
- Screenshots en cas d'échec
- Vidéos des tests
- Traces Playwright pour le débogage

---

##  Débogage

### Mode debug
```bash
# Tests avec interface graphique
pytest tests/test_playwright_e2e.py --headed

# Tests avec traces
pytest tests/test_playwright_e2e.py --tracing=on
```

### Commandes utiles
```bash
# Installation des navigateurs
playwright install

# Mise à jour des navigateurs
playwright install --force

# Codegen pour générer des tests
playwright codegen https://engravedetect.fr
```

---

##  Intégration CI/CD

### GitHub Actions
```yaml
# .github/workflows/playwright.yml
- name: Run Playwright E2E tests
  env:
    ENVIRONMENT: "test"
    TEST_URL: "https://engravedetect.fr"
    PLAYWRIGHT_BROWSER: "chromium"
    PLAYWRIGHT_HEADLESS: "true"
    PLAYWRIGHT_TIMEOUT: "30000"
  run: |
    python -m pytest tests/test_playwright_e2e.py -v --junitxml=test-results/results.xml
```

### Commentaires automatiques
- Résultats des tests postés sur les PR
- Statut de succès/échec
- Liens vers les artefacts de test

---

##  Bonnes pratiques

### Structure des tests
- Un test par fonctionnalité
- Tests indépendants
- Nettoyage après chaque test
- Utilisation de fixtures pour les données

### Sélecteurs robustes
```python
# Préférer les sélecteurs textuels
page.click('button:has-text("Se connecter")')

# Utiliser les attributs data-testid
page.click('[data-testid="login-button"]')

# Éviter les sélecteurs CSS fragiles
# page.click('.btn.btn-primary')  # Fragile
```

### Gestion des timeouts
```python
# Timeout personnalisé
page.set_default_timeout(30000)

# Attendre un élément
page.wait_for_selector('button:has-text("Se connecter")', timeout=10000)
```

---

##  Ressources

- [Documentation Playwright](https://playwright.dev/)
- [Guide des sélecteurs](https://playwright.dev/docs/selectors)
- [Tests d'accessibilité](https://playwright.dev/docs/accessibility-testing)
- [Configuration CI/CD](https://playwright.dev/docs/ci)

---

## 🆘 Support

En cas de problème :
1. Vérifier les logs dans GitHub Actions
2. Consulter les artefacts de test
3. Reproduire localement avec `--headed`
4. Utiliser les traces Playwright pour le débogage 