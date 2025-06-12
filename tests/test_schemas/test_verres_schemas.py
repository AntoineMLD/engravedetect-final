import pytest
from src.api.schemas.verres import VerreBase, VerreResponse, VerreFilters

def test_verre_base_valid():
    """Test la création d'un VerreBase avec données valides"""
    verre_data = {
        "nom": "Test Verre",
        "variante": "STANDARD",
        "hauteur_min": 20,
        "hauteur_max": 40,
        "indice": 1.5,
        "gravure": "ABC123",
        "protection": True,
        "photochromic": False
    }
    verre = VerreBase(**verre_data)
    assert verre.nom == "Test Verre"
    assert verre.variante == "STANDARD"
    assert verre.hauteur_min == 20
    assert verre.hauteur_max == 40
    assert verre.indice == 1.5
    assert verre.gravure == "ABC123"
    assert verre.protection is True
    assert verre.photochromic is False

def test_verre_base_minimal():
    """Test la création d'un VerreBase avec données minimales"""
    verre_data = {
        "nom": "Test Verre Minimal"
    }
    verre = VerreBase(**verre_data)
    assert verre.nom == "Test Verre Minimal"
    assert verre.variante is None
    assert verre.hauteur_min is None
    assert verre.hauteur_max is None
    assert verre.indice is None
    assert verre.gravure is None
    assert verre.protection is None
    assert verre.photochromic is None

def test_verre_base_invalid():
    """Test la validation des données invalides"""
    with pytest.raises(ValueError):
        VerreBase()  # nom manquant

def test_verre_response_valid():
    """Test la création d'un VerreResponse avec données valides"""
    verre_data = {
        "id": 1,
        "nom": "Test Verre",
        "fournisseur": "TestFournisseur",
        "materiau": "TestMateriau",
        "gamme": "TestGamme",
        "serie": "TestSerie",
        "variante": "STANDARD",
        "hauteur_min": 20,
        "hauteur_max": 40,
        "indice": 1.5,
        "gravure": "ABC123",
        "protection": True,
        "photochromic": False
    }
    verre = VerreResponse(**verre_data)
    assert verre.id == 1
    assert verre.nom == "Test Verre"
    assert verre.fournisseur == "TestFournisseur"
    assert verre.materiau == "TestMateriau"
    assert verre.gamme == "TestGamme"
    assert verre.serie == "TestSerie"

def test_verre_filters_valid():
    """Test la création de filtres valides"""
    filters_data = {
        "fournisseur": "TestFournisseur",
        "materiau": "TestMateriau",
        "gamme": "TestGamme",
        "serie": "TestSerie",
        "indice_min": 1.5,
        "indice_max": 1.7,
        "protection": True,
        "photochromic": False
    }
    filters = VerreFilters(**filters_data)
    assert filters.fournisseur == "TestFournisseur"
    assert filters.materiau == "TestMateriau"
    assert filters.indice_min == 1.5
    assert filters.indice_max == 1.7
    assert filters.protection is True
    assert filters.photochromic is False

def test_verre_filters_empty():
    """Test la création de filtres vides"""
    filters = VerreFilters()
    assert filters.fournisseur is None
    assert filters.materiau is None
    assert filters.gamme is None
    assert filters.serie is None
    assert filters.indice_min is None
    assert filters.indice_max is None
    assert filters.protection is None
    assert filters.photochromic is None 