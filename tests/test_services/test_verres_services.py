import pytest
from src.api.services import verres
from src.api.schemas.verres import VerreCreate, VerreUpdate
from src.api.models.verres import Verre


@pytest.fixture
def test_verre(db_session):
    """Crée un verre de test dans la base de données."""
    verre = Verre(
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
    db_session.add(verre)
    db_session.commit()
    db_session.refresh(verre)
    return verre


def test_create_verre(db_session):
    """Test de création d'un verre."""
    verre_data = VerreCreate(
        nom="Nouveau Verre",
        fournisseur="Test Fournisseur",
        materiaux="Test Materiaux",
        indice=1.5,
        protection=True,
        photochromic=False,
        hauteur_min=10.0,
        hauteur_max=20.0,
        gravure="TEST123",
    )

    result = verres.create_verre(db_session, verre_data)

    assert result.nom == verre_data.nom
    assert result.fournisseur == verre_data.fournisseur
    assert result.id is not None

    # Vérifier que le verre a bien été créé dans la base
    db_verre = db_session.query(Verre).filter(Verre.id == result.id).first()
    assert db_verre is not None
    assert db_verre.nom == verre_data.nom


def test_update_verre(db_session, test_verre):
    """Test de mise à jour d'un verre."""
    update_data = VerreUpdate(nom="Updated Verre", fournisseur="Updated Fournisseur")

    result = verres.update_verre(db_session, test_verre.id, update_data)

    assert result.nom == update_data.nom
    assert result.fournisseur == update_data.fournisseur

    # Vérifier que le verre a bien été mis à jour dans la base
    db_verre = db_session.query(Verre).filter(Verre.id == test_verre.id).first()
    assert db_verre.nom == update_data.nom


def test_update_verre_not_found(db_session):
    """Test de mise à jour d'un verre inexistant."""
    update_data = VerreUpdate(nom="Updated Verre", fournisseur="Updated Fournisseur")
    result = verres.update_verre(db_session, 999, update_data)
    assert result is None


def test_delete_verre(db_session, test_verre):
    """Test de suppression d'un verre."""
    result = verres.delete_verre(db_session, test_verre.id)
    assert result is True

    # Vérifier que le verre a bien été supprimé de la base
    db_verre = db_session.query(Verre).filter(Verre.id == test_verre.id).first()
    assert db_verre is None


def test_delete_verre_not_found(db_session):
    """Test de suppression d'un verre inexistant."""
    result = verres.delete_verre(db_session, 999)
    assert result is False


def test_get_verre_by_id(db_session, test_verre):
    """Test de récupération d'un verre par son ID."""
    result = verres.get_verre(db_session, test_verre.id)

    assert result is not None
    assert result.id == test_verre.id
    assert result.nom == test_verre.nom


def test_get_verre_by_id_not_found(db_session):
    """Test de récupération d'un verre inexistant."""
    result = verres.get_verre(db_session, 999)
    assert result is None
