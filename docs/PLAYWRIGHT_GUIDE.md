# Guide Playwright pour EngraveDetect

Ce guide explique comment utiliser Playwright pour les tests end-to-end dans le projet EngraveDetect.

## 🎯 Qu'est-ce que Playwright ?

Playwright est un framework de test automatisé pour les navigateurs web. Il permet de :
- Tester l'interface utilisateur de bout en bout
- Simuler les interactions utilisateur (clic, saisie, navigation)
- Tester sur différents navigateurs (Chrome, Firefox, Safari)
- Vérifier le comportement responsive
- Tester l'accessibilité

## 🚀 Installation rapide

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

## 📝 Structure des tests

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

## 🧪 Exécution des tests

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

## 📋 Exemples de tests

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
    expect(page.locator("text=📤 Déconnexion")).to_be_visible()
    expect(page.locator("h2:has-text('🎨 Dessiner une gravure')")).to_be_visible()
```

### Test de dessin sur canvas
```python
import os
from playwright.sync_api import Page, expect

@pytest.mark.playwright
def test_dessin_sur_canvas(page: Page):
    """Test du dessin sur le canvas"""
    # Connexion d'abord
    page.goto("https://engravedetect.fr")
    admin_username = os.getenv("ADMIN_USERNAME", "********")
    admin_password = os.getenv("ADMIN_PASSWORD", "******")
    page.fill('input[placeholder*="nom d\'utilisateur"]', admin_username)
    page.fill('input[placeholder*="mot de passe"]', admin_password)
    page.click('button:has-text("Se connecter")')
    
    # Localisation du canvas
    canvas = page.locator("canvas")
    canvas_box = canvas.bounding_box()
    
    if canvas_box:
        # Dessin d'une forme simple
        page.mouse.click(
            canvas_box["x"] + canvas_box["width"] / 2,
            canvas_box["y"] + canvas_box["height"] / 2
        )
        page.mouse.down()
        page.mouse.move(
            canvas_box["x"] + canvas_box["width"] / 2 + 50,
            canvas_box["y"] + canvas_box["height"] / 2 + 50
        )
        page.mouse.up()
```

### Test de recherche de symboles
```python
import os
from playwright.sync_api import Page, expect

@pytest.mark.playwright
def test_recherche_symboles(page: Page):
    """Test de recherche de symboles similaires"""
    # Connexion et dessin
    page.goto("https://engravedetect.fr")
    admin_username = os.getenv("ADMIN_USERNAME", "*****")
    admin_password = os.getenv("ADMIN_PASSWORD", "******")
    page.fill('input[placeholder*="nom d\'utilisateur"]', admin_username)
    page.fill('input[placeholder*="mot de passe"]', admin_password)
    page.click('button:has-text("Se connecter")')
    
    # Dessin sur le canvas
    canvas = page.locator("canvas")
    canvas_box = canvas.bounding_box()
    if canvas_box:
        page.mouse.click(canvas_box["x"] + 50, canvas_box["y"] + 50)
        page.mouse.down()
        page.mouse.move(canvas_box["x"] + 100, canvas_box["y"] + 100)
        page.mouse.up()
    
    # Recherche de symboles
    page.click('button:has-text("🔍 Rechercher les symboles similaires")')
    page.wait_for_timeout(3000)  # Attente des résultats
    
    # Vérification des résultats
    expect(page.locator("canvas")).to_be_visible()
```

## 🔧 Configuration avancée

### Variables d'environnement

Les tests Playwright utilisent les variables d'environnement suivantes :

```bash
# Identifiants d'administration
ADMIN_USERNAME=********
ADMIN_PASSWORD=*****

# URL du site à tester
TEST_URL=https://engravedetect.fr

# Configuration Playwright
PLAYWRIGHT_BROWSER=chromium
PLAYWRIGHT_HEADLESS=true
```

Pour configurer ces variables :

1. **Créer le fichier .env** :
   ```bash
   cp env.example .env
   ```

2. **Éditer le fichier .env** avec vos identifiants réels

3. **Vérifier la configuration** :
   ```bash
   python scripts/run_playwright_tests.py --list
   ```

### Configuration du navigateur
```python
# playwright.config.py
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    }
```

### Timeouts personnalisés
```python
def test_avec_timeout(page: Page):
    page.set_default_timeout(60000)  # 60 secondes
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")
```

### Gestion des erreurs
```python
def test_gestion_erreur(page: Page):
    try:
        page.goto("http://localhost:8000/page-inexistante")
    except Exception as e:
        # Gestion de l'erreur
        print(f"Erreur attendue: {e}")
    
    # Vérification de la page d'erreur
    expect(page.locator("h1")).to_contain_text("404")
```

## 🎨 Bonnes pratiques

### 1. Sélecteurs robustes
```python
# ❌ Fragile
page.locator("div:nth-child(3)")

# ✅ Robuste
page.locator('[data-testid="upload-button"]')
page.locator('button:has-text("Upload")')
page.locator('form[action="/upload"]')
```

### 2. Attentes explicites
```python
# ❌ Attente implicite
page.click("button")
page.locator(".result").to_be_visible()

# ✅ Attente explicite
page.click("button")
page.wait_for_selector(".result", state="visible")
expect(page.locator(".result")).to_be_visible()
```

### 3. Tests isolés
```python
@pytest.fixture(autouse=True)
def setup_test(page: Page):
    """Setup automatique pour chaque test"""
    page.goto("http://localhost:8000")
    yield
    # Cleanup si nécessaire
```

### 4. Gestion des données de test
```python
def test_avec_donnees(page: Page):
    # Utilisation de données de test
    test_image = "tests/test_data/test_image.jpg"
    
    # Vérification que le fichier existe
    assert Path(test_image).exists(), f"Fichier de test manquant: {test_image}"
    
    # Utilisation dans le test
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files(test_image)
```

## 🐛 Débogage

### Mode debug
```bash
# Lancer les tests en mode visible
pytest tests/test_playwright_e2e.py --headed

# Pause pour inspection
pytest tests/test_playwright_e2e.py --headed --pause
```

### Screenshots automatiques
```python
def test_avec_screenshot(page: Page):
    page.goto("http://localhost:8000")
    
    # Screenshot en cas d'échec
    if page.locator(".error").is_visible():
        page.screenshot(path="error_screenshot.png")
        raise Exception("Erreur détectée")
```

### Traces Playwright
```bash
# Générer une trace
pytest tests/test_playwright_e2e.py --tracing=on

# Visualiser la trace
playwright show-trace trace.zip
```

## 📊 Intégration CI/CD

### Configuration GitHub Actions
```yaml
# .github/workflows/ci.yml
- name: Install Playwright
  run: |
    pip install playwright pytest-playwright
    playwright install

- name: Run Playwright tests
  run: |
    pytest tests/test_playwright_e2e.py -v
```

### Variables d'environnement
```bash
# URL de test
TEST_URL=https://engravedetect.fr

# Identifiants de test
ADMIN_USERNAME=admin
ADMIN_PASSWORD=adminpass123

# Navigateur par défaut
PLAYWRIGHT_BROWSER=chromium

# Mode headless
PLAYWRIGHT_HEADLESS=true
```

## 🔍 Monitoring et reporting

### Métriques de performance
```python
def test_performance(page: Page):
    start_time = time.time()
    
    page.goto("http://localhost:8000")
    page.wait_for_load_state("networkidle")
    
    load_time = time.time() - start_time
    assert load_time < 3.0, f"Temps de chargement: {load_time:.2f}s"
```

### Rapports de couverture
```bash
# Couverture des tests Playwright
pytest tests/test_playwright_e2e.py --cov=src/front --cov-report=html
```

## 📚 Ressources utiles

- [Documentation officielle Playwright](https://playwright.dev/python/)
- [Guide pytest-playwright](https://github.com/microsoft/playwright-python)
- [Sélecteurs CSS](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- [Accessibilité](https://www.w3.org/WAI/WCAG21/quickref/)

## 🆘 Dépannage

### Problèmes courants

1. **Navigateur non trouvé**
   ```bash
   playwright install
   ```

2. **Tests qui échouent en CI**
   ```bash
   # Utiliser des arguments de navigateur spécifiques
   playwright install --with-deps
   ```

3. **Timeouts fréquents**
   ```python
   page.set_default_timeout(60000)  # Augmenter le timeout
   ```

4. **Sélecteurs instables**
   ```python
   # Utiliser des sélecteurs plus robustes
   page.locator('[data-testid="button"]')
   ```

### Support
- Vérifier les logs de test
- Utiliser le mode debug (`--headed`)
- Consulter la documentation Playwright
- Créer une issue sur le repository 