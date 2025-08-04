# test_model.py

import pytest
import torch
from torch import nn
from torch.nn import functional as F

# Import conditionnel du modèle
try:
    from src.models.efficientnet_triplet import EfficientNetEmbedding
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


@pytest.fixture(scope="module")
def model(torch_available):
    """Initialise un modèle avec embedding_dim=128 sans poids préentraînés pour les tests."""
    if not torch_available:
        pytest.skip("PyTorch/TorchVision non compatibles")
    return EfficientNetEmbedding(embedding_dim=128, pretrained=False)


@pytest.mark.torch
def test_grayscale_conversion(model):
    """Vérifie que l'adaptation grayscale → RGB produit un tenseur à 3 canaux."""
    x = torch.randn(4, 1, 224, 224)
    out = model.grayscale_conv(x)
    assert out.shape == (4, 3, 224, 224), "La conversion grayscale → RGB échoue."


@pytest.mark.torch
def test_forward_one_shape_and_l2_norm(model):
    """Teste la sortie de forward_one (forme et normalisation L2)."""
    x = torch.randn(2, 1, 224, 224)
    emb = model.forward_one(x)
    assert emb.shape == (2, 128), "La sortie embedding a une forme incorrecte."
    norms = emb.norm(p=2, dim=1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-4), "L'embedding n'est pas normalisé L2."


@pytest.mark.torch
def test_forward_triplet_output(model):
    """Vérifie que le forward triplet retourne bien 3 embeddings cohérents."""
    x = torch.randn(4, 1, 224, 224)
    anchor, positive, negative = model(x, x, x)
    assert anchor.shape == positive.shape == negative.shape == (4, 128), "La forme des triplets est incorrecte."


@pytest.mark.torch
def test_requires_grad(model):
    """S'assure que tous les paramètres ont bien requires_grad à True."""
    for name, param in model.named_parameters():
        assert param.requires_grad, f"Le paramètre {name} ne permet pas le calcul du gradient."


@pytest.mark.torch
def test_model_end_to_end(model):
    """Vérifie un passage complet sur des données factices."""
    batch = torch.randn(8, 1, 224, 224)
    output = model.forward_one(batch)
    assert isinstance(output, torch.Tensor), "La sortie n'est pas un tenseur."
    assert output.shape == (8, 128), "La forme de la sortie est incorrecte."


@pytest.mark.torch
def test_model_init_without_pretrained():
    """Vérifie que le modèle s'initialise sans poids préentraînés."""
    try:
        EfficientNetEmbedding(embedding_dim=64, pretrained=False)
    except Exception as e:
        pytest.fail(f"Échec d'initialisation sans pretrained : {e}")
