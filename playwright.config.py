"""
Configuration Playwright pour les tests end-to-end
"""

from playwright.sync_api import Playwright, expect, sync_playwright


def run(playwright: Playwright) -> None:
    """
    Configuration de base pour Playwright
    """
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Configuration par défaut
    page.set_default_timeout(30000)  # 30 secondes
    page.set_default_navigation_timeout(30000)

    return browser, context, page


# Configuration pour pytest-playwright
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Configuration du contexte navigateur pour tous les tests
    """
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "ignore_https_errors": True,
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    }


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """
    Arguments de lancement du navigateur
    """
    return {
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
        ],
    }
