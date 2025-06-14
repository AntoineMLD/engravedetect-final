import pytest
from unittest.mock import MagicMock
from src.api.schemas.verres import VerreCreate, VerreUpdate, VerreFilters
from src.api.services.verres import (
    create_verre,
    update_verre,
    delete_verre,
    get_verres,
    get_verre,
    get_fournisseurs,
    get_materiaux,
    get_stats,
)
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
        gravure="TEST123",
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
    db.refresh.side_effect = lambda x: setattr(x, "id", 1)
    return db


def test_create_verre(mock_db):
    """Test de création d'un verre."""
    verre_data = VerreCreate(
        nom="Test Verre",
        fournisseur="Test Fournisseur",
        materiaux="Test Materiaux",
        indice=1.5,
        protection=True,
        photochromic=False,
        hauteur_min=10.0,
        hauteur_max=20.0,
        gravure="TEST123",
    )

    # Configuration du mock pour simuler la création
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    result = create_verre(mock_db, verre_data)
    assert result.nom == verre_data.nom
    assert result.fournisseur == verre_data.fournisseur
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_verre(mock_db, mock_verre):
    """Test de mise à jour d'un verre."""
    verre_id = 1
    update_data = VerreUpdate(nom="Updated Verre", fournisseur="Updated Fournisseur")

    # Configuration du mock pour simuler la mise à jour
    mock_db.query.return_value.filter.return_value.first.return_value = mock_verre
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    result = update_verre(mock_db, verre_id, update_data)
    assert result.nom == update_data.nom
    assert result.fournisseur == update_data.fournisseur
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_verre_not_found(mock_db):
    """Test de mise à jour d'un verre inexistant."""
    verre_id = 999
    update_data = VerreUpdate(nom="Updated Verre", fournisseur="Updated Fournisseur")

    # Configuration du mock pour simuler un verre non trouvé
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = update_verre(mock_db, verre_id, update_data)
    assert result is None


def test_delete_verre(mock_db, mock_verre):
    """Test de suppression d'un verre."""
    verre_id = 1

    # Configuration du mock pour simuler la suppression
    mock_db.query.return_value.filter.return_value.first.return_value = mock_verre
    mock_db.delete = MagicMock()
    mock_db.commit = MagicMock()

    result = delete_verre(mock_db, verre_id)
    assert result is True
    mock_db.delete.assert_called_once_with(mock_verre)
    mock_db.commit.assert_called_once()


def test_delete_verre_not_found(mock_db):
    """Test de suppression d'un verre inexistant."""
    verre_id = 999

    # Configuration du mock pour simuler un verre non trouvé
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = delete_verre(mock_db, verre_id)
    assert result is False


def test_get_verres_with_filters(mock_db, mock_verre):
    """Test de récupération des verres avec filtres."""
    filters = VerreFilters(fournisseur="Test Fournisseur", indice_min=1.0, indice_max=2.0, protection=True)

    # Configuration du mock pour simuler la récupération
    mock_db.query.return_value.filter.return_value.count.return_value = 1
    mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
        mock_verre
    ]

    result = get_verres(mock_db, filters)
    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].nom == mock_verre.nom


def test_get_verre_by_id(mock_db, mock_verre):
    """Test de récupération d'un verre par son ID."""
    verre_id = 1

    # Configuration du mock pour simuler la récupération
    mock_db.query.return_value.filter.return_value.first.return_value = mock_verre

    result = get_verre(mock_db, verre_id)
    assert result is not None
    assert result.id == mock_verre.id
    assert result.nom == mock_verre.nom


def test_get_verre_by_id_not_found(mock_db):
    """Test de récupération d'un verre inexistant."""
    verre_id = 999

    # Configuration du mock pour simuler un verre non trouvé
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_verre(mock_db, verre_id)
    assert result is None
