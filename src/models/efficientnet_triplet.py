import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models


class EfficientNetEmbedding(nn.Module):
    """
    Modèle PyTorch basé sur EfficientNet-B0 pour l'extraction d'embeddings à partir d'images.

    Ce modèle est conçu pour fonctionner avec des images en niveaux de gris (grayscale)
    et pour être utilisé dans des architectures à Triplet Loss.

    Args:
        embedding_dim (int): Dimension de l'espace d'embedding de sortie.
        pretrained (bool): Si True, charge les poids pré-entraînés ImageNet.

    Exemple d'utilisation :
        model = EfficientNetEmbedding(embedding_dim=256, pretrained=True)
        emb = model.forward_one(image_tensor)
    """

    def __init__(self, embedding_dim: int = 256, pretrained: bool = True):
        """
        Initialise le modèle EfficientNetEmbedding.

        Args:
            embedding_dim (int): Dimension de l'embedding de sortie.
            pretrained (bool): Charge les poids ImageNet si True.
        """
        super().__init__()

        # charge EfficientNet-B0 avec les poids appropriés
        if pretrained:
            self.backbone = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        else:
            self.backbone = models.efficientnet_b0(weights=None)

        # récupère la dimension du backbone
        last_channel = self.backbone.classifier[1].in_features

        # supprime la tête de classification
        self.backbone.classifier = nn.Identity()

        # Tête MLP pour projeter les features en vecteurs d'embedding
        self.embedding_head = nn.Sequential(
            nn.Linear(last_channel, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, embedding_dim),
        )

        # Adaptateur pour convertir des images 1 canal (grayscale) en 3 canaux
        self.grayscale_conv = nn.Conv2d(1, 3, kernel_size=1)
        nn.init.kaiming_normal_(self.grayscale_conv.weight)

    def forward_one(self, x: torch.Tensor) -> torch.Tensor:
        """
        Calcule l'embedding d'une seule image ou d'un batch d'images.

        Args:
            x (torch.Tensor): Image ou batch d'images de forme (B, 1, H, W) en niveaux de gris.

        Returns:
            torch.Tensor: Embedding normalisé L2 de forme (B, embedding_dim).

        Exemple d'utilisation :
            emb = model.forward_one(image_tensor)
        """
        if x.size(1) == 1:
            x = self.grayscale_conv(x)

        features = self.backbone(x)
        embedding = self.embedding_head(features)
        embedding = F.normalize(embedding, p=2, dim=1)
        return embedding

    def forward(self, anchor, positive, negative):
        """
        Calcule les embeddings pour un triplet (anchor, positive, negative).
        Utilisé pour la compatibilité avec la Triplet Loss.

        Args:
            anchor (torch.Tensor): Batch d'images ancre.
            positive (torch.Tensor): Batch d'images positives.
            negative (torch.Tensor): Batch d'images négatives.

        Returns:
            Tuple[torch.Tensor, torch.Tensor, torch.Tensor]: Embeddings normalisés pour anchor, positive, negative.

        Exemple d'utilisation :
            anchor_emb, pos_emb, neg_emb = model(anchor, positive, negative)
        """
        anchor_emb = self.forward_one(anchor)
        positive_emb = self.forward_one(positive)
        negative_emb = self.forward_one(negative)

        return anchor_emb, positive_emb, negative_emb
