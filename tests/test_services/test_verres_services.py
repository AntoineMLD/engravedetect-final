import pytest
from unittest.mock import MagicMock
from src.api.schemas.verres import VerreCreate, VerreUpdate
from src.api.services.verres import create_verre, update_verre, delete_verre, get_verres, get_verre
from src.api.models.verres import Verre

class MockVerre:
    """Classe qui simule un objet SQLAlchemy pour les tests."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

@pytest.fixture
def mock_verre():
    """Mock d'un verre pour les tests."""
    return MockVerre(
        id=1,
        nom="Test Verre",
        fournisseur="Test Fournisseur",
        materiaux="Test Materiaux",
        indice=1.5,
        protection=True,
        photochromic=False,
        hauteur_min=10.0,
        hauteur_max=20.0,
        gravure="TEST123"
    )

@pytest.fixture
def mock_db(mock_verre):
    """Crée une session de base de données mockée avec un verre."""
    db = MagicMock()
    # Configuration du mock pour get_verre
    db.query.return_value.filter.return_value.first.return_value = mock_verre
    # Configuration du mock pour get_verres
    db.query.return_value.filter.return_value.count.return_value = 1
    db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [mock_verre]
    # Configuration du mock pour create_verre
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = lambda x: setattr(x, 'id', 1)
    return db

def test_create_verre(mock_db, mock_verre):
    """Test de création d'un verre."""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, 'id', 1)
    
    verre_data = VerreCreate(
        nom="Test Verre",
        fournisseur="Test Fournisseur",
        materiaux="Test Materiaux",
        indice=1.5,
        protection=True,
        photochromic=False,
        hauteur_min=10.0,
        hauteur_max=20.0,
        gravure="TEST123"
    )
    
    result = create_verre(mock_db, verre_data)
    assert result.nom == "Test Verre"

def test_update_verre(mock_db, mock_verre):
    """Test de mise à jour d'un verre."""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_verre
    mock_db.commit.return_value = None
    
    verre_data = VerreUpdate(nom="Updated Verre")
    result = update_verre(mock_db, 1, verre_data)
    assert result.nom == "Updated Verre"

def test_delete_verre(mock_db, mock_verre):
    """Test de suppression d'un verre."""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_verre
    mock_db.delete.return_value = None
    mock_db.commit.return_value = None
    
    result = delete_verre(mock_db, 1)
    assert result is True

def test_get_verres(mock_db, mock_verre):
    """Test de récupération des verres."""
    # Configuration du mock pour la requête
    query_mock = MagicMock()
    query_mock.count.return_value = 1
    query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_verre]
    mock_db.query.return_value = query_mock
    
    result = get_verres(mock_db)
    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].nom == "Test Verre"

def test_get_verre_by_id(mock_db, mock_verre):
    """Test de récupération d'un verre par son ID."""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_verre
    
    result = get_verre(mock_db, 1)
    assert result.nom == "Test Verre" 