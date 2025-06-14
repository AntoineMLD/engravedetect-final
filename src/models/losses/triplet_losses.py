import torch
import torch.nn as nn
import torch.nn.functional as F

class TripletLoss(nn.Module):
    """
    Triplet Margin Loss standard basée sur des triplets (anchor, positive, negative) déjà formés.
    """
    def __init__(self, margin: float = 0.3):
        super().__init__()
        self.margin = margin 
        self.ranking_loss = nn.MarginRankingLoss(margin=margin)

    def forward(self, anchor: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor) -> torch.Tensor:
        dist_pos = torch.sum((anchor - positive) ** 2, dim=1)
        dist_neg = torch.sum((anchor - negative) ** 2, dim=1)
        target = torch.ones_like(dist_pos)
        loss = self.ranking_loss(dist_neg, dist_pos, target)
        return loss
    

class HardTripletLoss(nn.Module):
    """
    Triplet Loss avec mining dynamique des trilplets les plus difficiles dans un batch.
    """
    def __init__(self, margin : float = 0.3, mining_type: str ='semi-hard'):
        super().__init__()
        assert mining_type in ['hard', 'semi-hard', 'all'], "mining_type doit être 'hard', 'semi-hard' ou 'all'"
        self.margin = margin
        self.mining_type = mining_type

    def forward(self, anchor: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor) -> torch.Tensor:
        """
        Calcule la Triplet Loss avec mining dynamique.
        
        Args:
        anchor: Tensor de forme (B, D) - embeddings des ancres
        positive: Tensor de forme (B, D) - embeddings des exemples positifs
        negative: Tensor de forme (B, D) - embeddings des exemples négatifs
        
        Returns:
        Loss moyenne sur tous les triplets valides
        """
        # Calcul des distances euclidiennes
        dist_pos = torch.sum((anchor - positive) ** 2, dim=1)
        dist_neg = torch.sum((anchor - negative) ** 2, dim=1)
        
        # Calcul de la loss selon le type de mining
        if self.mining_type == 'hard':
            # Hard mining: on prend le triplet le plus difficile
            loss = F.relu(dist_pos - dist_neg + self.margin)
        elif self.mining_type == 'semi-hard':
            # Semi-hard mining: on prend les triplets qui sont difficiles mais pas impossibles
            # On ne garde que les triplets où dist_neg > dist_pos et dist_neg < dist_pos + margin
            mask = (dist_neg > dist_pos) & (dist_neg < dist_pos + self.margin)
            if mask.any():
                loss = F.relu(dist_pos[mask] - dist_neg[mask] + self.margin)
            else:
                # Si aucun triplet semi-hard n'est trouvé, on utilise le triplet le plus difficile
                loss = F.relu(dist_pos - dist_neg + self.margin)
        else:  # 'all'
            # On utilise tous les triplets
            loss = F.relu(dist_pos - dist_neg + self.margin)
        
        return loss.mean()
    
