import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models


class EfficientNetEmbedding(nn.Module):
    """
    Modèle basé sur EfficientNet-B0 pour l'extraction d'embedding.
    Conçu pour fonctionner avec des images grayscale et compatible Triplet Loss.
    """

    def __init__(self, embedding_dim: int = 256, pretrained: bool = True):
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
        Calcule l'embedding d'une seule image ou un batch.

        Args:
        x: image grayscale tensor de forme (B, 1, H, W)

        Returns:
        embedding normalisé L2 de forme (B, embedding_dim)
        """

        if x.size(1) == 1:
            x = self.grayscale_conv(x)

        features = self.backbone(x)
        embedding = self.embedding_head(features)
        embedding = F.normalize(embedding, p=2, dim=1)
        return embedding

    def forward(self, anchor, positive, negative):
        """
        Pour compatibilité avec Triplet Loss.
        """
        anchor_emb = self.forward_one(anchor)
        positive_emb = self.forward_one(positive)
        negative_emb = self.forward_one(negative)

        return anchor_emb, positive_emb, negative_emb
