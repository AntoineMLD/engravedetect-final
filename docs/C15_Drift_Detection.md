# C15. Détection de Drift - Guide Complet

## Contexte et Objectifs

La détection de drift dans EngraveDetect permet d'identifier les changements dans la distribution des données d'entrée qui pourraient affecter les performances du modèle d'IA. Ce système utilise une approche basée sur une baseline historique pour détecter les dérives de manière réaliste et actionable.

---

## Principe de Fonctionnement

### Concept du Drift
Le **drift** (ou dérive) se produit quand les données d'entrée actuelles diffèrent significativement des données utilisées pour entraîner le modèle. Cela peut causer :
- Baisse de l'accuracy
- Prédictions incorrectes
- Perte de confiance dans le modèle

### Approche EngraveDetect
1. **Baseline historique** : Collecte d'embeddings de référence
2. **Comparaison continue** : Analyse des nouveaux embeddings vs baseline
3. **Score normalisé** : Métrique entre 0 et 1 pour quantifier le drift

---

## Architecture Technique

### Composants
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nouvel        │    │   Baseline      │    │   Score de      │
│   Embedding     │───▶│   Historique    │───▶│   Drift         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
   Extraction          50 embeddings          Distance
   Features            de référence          normalisée
```

### Implémentation
- **Langage** : Python avec NumPy
- **Métrique** : Distance euclidienne normalisée
- **Lissage** : Fonction sigmoïde pour stabiliser les scores
- **Stockage** : Métrique Prometheus `model_drift_score`

---

## Phases de Détection

### Phase 1 : Établissement de la Baseline (0-50 requêtes)

#### Comportement
- **Score de drift** : 0.5 (neutre)
- **Couleur Grafana** : Jaune
- **Action** : Collecte d'embeddings de référence

#### Code
```python
if not self.baseline_established:
    self.baseline_embeddings.append(embedding.copy())
    
    if len(self.baseline_embeddings) >= self.baseline_size:
        self.baseline_established = True
        logger.info(f"Baseline établie avec {len(self.baseline_embeddings)} embeddings")
    
    return 0.5  # Score neutre pendant l'établissement
```

#### Vérification
```bash
curl http://localhost:8001/model/health | jq '.model_metrics.drift_baseline_established'
# false pendant la phase 1
```

### Phase 2 : Détection Active (50+ requêtes)

#### Comportement
- **Score de drift** : 0.0 - 1.0 (basé sur la distance réelle)
- **Couleur Grafana** : Vert/Jaune/Rouge selon le score
- **Action** : Comparaison avec la baseline établie

#### Calcul du Score
```python
def _calculate_drift_vs_baseline(self, embedding: np.ndarray) -> float:
    # Statistiques de la baseline
    baseline_mean = np.mean(baseline_array, axis=0)
    baseline_std = np.std(baseline_array, axis=0)
    
    # Distances normalisées
    mean_distance = np.linalg.norm(embedding - baseline_mean)
    std_distance = np.linalg.norm(np.abs(embedding - baseline_mean) - baseline_std)
    
    # Normalisation
    mean_distance_norm = mean_distance / (np.linalg.norm(baseline_mean) + 1e-6)
    std_distance_norm = std_distance / (np.linalg.norm(baseline_std) + 1e-6)
    
    # Score final avec lissage sigmoïde
    drift_score = min(1.0, (mean_distance_norm + std_distance_norm) / 2.0)
    drift_score = 1.0 / (1.0 + math.exp(-10 * (drift_score - 0.5)))
    
    return drift_score
```

---

## Interprétation des Scores

### Échelle de Drift
| Score | Couleur | Signification | Action Recommandée |
|-------|---------|---------------|-------------------|
| **0.0 - 0.3** | 🟢 Vert | **Excellent** - Aucun drift | Continuer la surveillance |
| **0.3 - 0.5** | 🟡 Jaune | **Bon** - Drift léger | Surveiller l'évolution |
| **0.5 - 0.7** | 🟠 Orange | **Attention** - Drift modéré | Analyser les causes |
| **0.7 - 1.0** | 🔴 Rouge | **Problème** - Drift élevé | Intervention requise |

### Seuils d'Alerte
```python
# Configuration dans model_monitoring.py
self.drift_threshold = 0.7  # Seuil d'alerte critique
```

### Logs Automatiques
```python
if drift_score > self.drift_threshold:
    logger.warning(f"Drift élevé détecté: {drift_score:.3f} (seuil: {self.drift_threshold})")
```

---

## Configuration

### Paramètres Modifiables
```python
class ModelMonitor:
    def __init__(self):
        # Taille de la baseline
        self.baseline_size = 50  # Nombre d'embeddings pour la baseline
        
        # Seuils de détection
        self.drift_threshold = 0.7  # Seuil d'alerte
        self.drift_check_probability = 0.1  # 10% des requêtes
        
        # Intervalle de vérification
        self.drift_check_interval = timedelta(minutes=5)
```

### Optimisations Possibles
```python
# Pour un monitoring plus fréquent
self.drift_check_probability = 0.3  # 30% des requêtes
self.drift_check_interval = timedelta(minutes=1)

# Pour une baseline plus robuste
self.baseline_size = 100  # Plus d'embeddings de référence

# Pour des seuils plus stricts
self.drift_threshold = 0.5  # Alerte plus précoce
```

---

## Monitoring et Alertes

### Métriques Exposées
```bash
# Score de drift actuel
curl http://localhost:8001/metrics | grep model_drift_score

# État de la baseline
curl http://localhost:8001/model/health | jq '.model_metrics.drift_baseline_established'
```

### Dashboard Grafana
- **Panel** : "Drift Detection"
- **Type** : Jauge avec seuils colorés
- **Métrique** : `model_drift_score`
- **Rafraîchissement** : 30 secondes

### Alertes Prometheus
```yaml
- alert: ModelDriftHigh
  expr: model_drift_score > 0.7
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Drift élevé détecté"
    description: "Le score de drift a dépassé le seuil de 0.7"
    dashboard: "http://localhost:3001/d/engravedetect-dashboard"
```

---

## Tests et Validation

### Scripts de Test Disponibles

#### 1. Test de Drift avec Images Diverses
```bash
python3 scripts/test_drift_detection.py
```
**Objectif** : Maximiser les chances de détecter du drift
- 30 images différentes
- 3 cycles de test
- 90 requêtes totales

#### 2. Debug de la Détection
```bash
python3 scripts/debug_drift.py
```
**Objectif** : Diagnostic des problèmes de drift
- Vérification des métriques
- Test de la santé du modèle
- Analyse des logs

#### 3. Génération de Données de Test
```bash
python3 scripts/generate_test_data.py
```
**Objectif** : Générer des données pour établir la baseline
- 10 requêtes avec pauses
- Gestion du rate limiting
- Images de test automatiques

### Validation Manuelle
```bash
# 1. Vérifier l'état initial
curl http://localhost:8001/model/health | jq '.model_metrics.drift_baseline_established'

# 2. Faire des requêtes
python3 scripts/generate_test_data.py

# 3. Vérifier l'évolution
curl http://localhost:8001/model/health | jq '.model_metrics'

# 4. Observer dans Grafana
# http://localhost:3001
```

---

## Cas d'Usage

### Scénario 1 : Drift Léger (0.3 - 0.5)
**Situation** : Nouveaux types d'images légèrement différents
**Action** : Surveillance renforcée, pas d'intervention immédiate

### Scénario 2 : Drift Modéré (0.5 - 0.7)
**Situation** : Changement significatif dans les données
**Action** : Analyse des causes, évaluation de l'impact

### Scénario 3 : Drift Élevé (0.7 - 1.0)
**Situation** : Dérive majeure détectée
**Action** : Intervention immédiate, possible retraining du modèle

---

## Maintenance et Optimisation

### Réinitialisation de la Baseline
```python
# Pour forcer une nouvelle baseline
self.baseline_embeddings = []
self.baseline_established = False
```

### Ajustement des Seuils
```python
# Seuils plus stricts pour la production
self.drift_threshold = 0.6  # Alerte plus précoce
self.drift_check_probability = 0.2  # Vérification plus fréquente
```

### Sauvegarde de l'Historique
```python
# Sauvegarder l'historique des scores
import json
with open('drift_history.json', 'w') as f:
    json.dump(self.drift_history, f)
```

---

## Dépannage

### Problèmes Courants

#### 1. Baseline non établie
**Symptôme** : Score toujours à 0.5
**Solution** : Faire plus de requêtes (minimum 50)

#### 2. Pas de drift détecté
**Symptôme** : Score toujours bas (< 0.3)
**Cause** : Données très similaires
**Solution** : Normal, le modèle est stable

#### 3. Drift élevé persistant
**Symptôme** : Score > 0.7
**Action** : Analyser les nouvelles données, considérer un retraining

### Logs de Debug
```bash
# Vérifier les logs de l'API IA
docker compose logs api_ia | grep -i drift

# Vérifier les métriques
curl http://localhost:8001/metrics | grep model_drift
```

---

## Conclusion

La détection de drift d'EngraveDetect offre une surveillance proactive des changements dans les données d'entrée. L'approche basée sur une baseline historique fournit des métriques réalistes et actionnables pour maintenir la qualité du modèle en production.

Le système est configurable, testable et intégré dans l'architecture de monitoring existante, permettant une détection précoce des problèmes et une maintenance préventive du modèle d'IA. 