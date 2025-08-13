# C14. Monitoring de l'API d'Intelligence Artificielle

## Table des Matières
- [Contexte et Objectifs](#contexte-et-objectifs)
- [Architecture de Monitoring](#architecture-de-monitoring)
  - [Stack Technologique](#stack-technologique)
  - [Architecture](#architecture)
- [Métriques Exposées](#métriques-exposées)
  - [Métriques de Performance](#1-métriques-de-performance)
  - [Métriques de Qualité](#2-métriques-de-qualité)
  - [Métriques d'Embedding](#3-métriques-dembedding)
  - [Métriques de Drift](#4-métriques-de-drift)
- [Endpoints de Monitoring](#endpoints-de-monitoring)
- [Configuration Prometheus](#configuration-prometheus)
- [Dashboard Grafana](#dashboard-grafana)
- [Détection de Drift](#détection-de-drift)
- [Alertes Prometheus](#alertes-prometheus)
- [Scripts de Test](#scripts-de-test)
- [Dépannage](#dépannage)

---

## Contexte et Objectifs

Le monitoring de l'API IA EngraveDetect permet de surveiller en temps réel les performances du modèle, détecter les dérives de données (drift) et assurer la qualité du service. Le système utilise Prometheus pour la collecte de métriques et Grafana pour la visualisation.

---

## Architecture de Monitoring

### Stack Technologique
- **Prometheus** : Collecte et stockage des métriques
- **Grafana** : Visualisation et alertes
- **FastAPI** : Exposition des métriques via `/metrics`
- **Prometheus Client Python** : Instrumentation de l'application

### Architecture

**Diagramme de l'architecture de monitoring :**

```mermaid
graph LR
    A[API IA<br/>Port 8001] --> B[Prometheus<br/>Port 9090]
    B --> C[Grafana<br/>Port 3001]
    
    A1[/metrics endpoint] --> A
    B1[Time Series DB] --> B
    C1[Dashboards] --> C
```

*Description : L'API IA expose ses métriques via l'endpoint /metrics, Prometheus collecte et stocke ces données dans sa base de données temporelle, et Grafana visualise les métriques via des tableaux de bord.*

---

## Métriques Exposées

### 1. Métriques de Performance

#### Prédictions
- `model_predictions_total` : Nombre total de prédictions
- `model_predictions_success` : Prédictions réussies
- `model_predictions_failed` : Prédictions échouées

#### Temps de réponse
- `model_inference_time_seconds` : Temps d'inférence (histogramme)
- `model_throughput` : Débit de prédictions par minute

#### Requêtes API
- `match_requests_total` : Total des requêtes `/match`
- `match_latency_seconds` : Latence des requêtes `/match`
- `embedding_requests_total` : Total des requêtes `/embedding`
- `embedding_latency_seconds` : Latence des requêtes `/embedding`

### 2. Métriques de Qualité

#### Accuracy
- `model_top1_accuracy` : Top-1 accuracy (classe prédite correcte)
- `model_top3_accuracy` : Top-3 accuracy (classe correcte dans top 3)

#### Confiance
- `model_prediction_confidence` : Distribution de la confiance (histogramme)
- `model_confidence_high` : Prédictions avec confiance élevée (>0.8)
- `model_confidence_medium` : Prédictions avec confiance moyenne (0.5-0.8)
- `model_confidence_low` : Prédictions avec confiance faible (<0.5)

#### Rejet
- `model_rejection_rate` : Taux de rejet (confiance < seuil)

### 3. Métriques d'Embedding

#### Qualité
- `model_embedding_quality` : Qualité des embeddings générés
- `model_embedding_normality` : Normalité des embeddings (test Shapiro-Wilk)
- `model_feature_activation` : Activité moyenne des features

### 4. Métriques de Drift

#### Détection de Drift
- `model_drift_score` : Score de drift des données d'entrée

---

## Endpoints de Monitoring

### 1. `/metrics` (GET)
**Description** : Exposition des métriques Prometheus

**Accès** : Public (pas d'authentification requise)

**Réponse** : Format Prometheus
```bash
# HELP model_predictions_total Nombre total de prédictions
# TYPE model_predictions_total counter
model_predictions_total{model_name="engravedetect_efficientnet",status="success"} 62.0

# HELP model_drift_score Score de drift des données d'entrée
# TYPE model_drift_score gauge
model_drift_score{model_name="engravedetect_efficientnet"} 0.234
```

**Exemple d'utilisation** :
```bash
curl http://localhost:8001/metrics
```

### 2. `/model/health` (GET)
**Description** : Statut de santé du modèle IA

**Accès** : Public

**Réponse** :
```json
{
  "status": "healthy",
  "model_metrics": {
    "model_name": "engravedetect_efficientnet",
    "total_predictions": 62,
    "success_count": 62,
    "top1_accuracy": 1.0,
    "top3_accuracy": 0.733,
    "rejection_rate": 0.0,
    "confidence_distribution": {
      "high": 3,
      "medium": 12,
      "low": 0
    },
    "average_inference_time": 0.125,
    "average_confidence": 0.762,
    "average_embedding_quality": 0.340,
    "current_throughput": 11.62,
    "drift_baseline_established": true,
    "drift_baseline_size": 50,
    "drift_history_size": 10,
    "average_drift_score": 0.234
  },
  "timestamp": "2025-08-05T10:35:16.954209"
}
```

**Exemple d'utilisation** :
```bash
curl http://localhost:8001/model/health | jq
```

---

## Configuration Prometheus

### Fichier de configuration : `monitoring/prometheus/prometheus.yml`
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'api_ia'
    static_configs:
      - targets: ['api_ia:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Métriques collectées automatiquement
- Toutes les métriques exposées par `/metrics`
- Intervalle de collecte : 30 secondes
- Rétention : 15 jours (configurable)

---

## Dashboard Grafana

### Dashboard principal : `monitoring/grafana/engravedetect_dashboard.json`

#### Panels inclus :
1. **Volume de Prédictions** : Graphique linéaire des prédictions totales
2. **Prédictions Confiance Moyenne** : Statistique des prédictions avec confiance moyenne
3. **Top-1 Accuracy** : Jauge de l'accuracy Top-1
4. **Top-3 Accuracy** : Jauge de l'accuracy Top-3
5. **Temps d'Inférence (P95)** : Graphique des temps de réponse
6. **Drift Detection** : Jauge du score de drift
7. **Qualité des Embeddings** : Jauge de la qualité des embeddings

#### Seuils d'alerte :
- **Top-1 Accuracy** : < 0.8 (rouge)
- **Top-3 Accuracy** : < 0.9 (rouge)
- **Drift Detection** : > 0.7 (rouge)
- **Temps d'Inférence** : > 2s (rouge)

---

## Détection de Drift

### Principe de fonctionnement
1. **Phase baseline** (0-50 requêtes) : Collecte d'embeddings de référence
2. **Phase détection** (50+ requêtes) : Comparaison avec la baseline
3. **Calcul du score** : Distance normalisée entre embedding actuel et baseline

### Interprétation des scores
- **0.0 - 0.3** :  **Excellent** - Aucun drift détecté
- **0.3 - 0.5** :  **Bon** - Drift léger
- **0.5 - 0.7** :  **Attention** - Drift modéré
- **0.7 - 1.0** :  **Problème** - Drift élevé

### Configuration
```python
# Dans model_monitoring.py
self.baseline_size = 50  # Nombre d'embeddings pour la baseline
self.drift_threshold = 0.7  # Seuil d'alerte
self.drift_check_probability = 0.1  # 10% des requêtes
```

---

## Alertes Prometheus

### Fichier de configuration : `monitoring/prometheus/model_alerts.yml`

#### Alertes configurées :
1. **ModelTop1AccuracyDegradation** : Top-1 accuracy < 0.8
2. **ModelTop3AccuracyDegradation** : Top-3 accuracy < 0.9
3. **ModelRejectionRateHigh** : Taux de rejet > 0.2
4. **ModelDriftHigh** : Score de drift > 0.7

#### Exemple d'alerte :
```yaml
- alert: ModelTop1AccuracyDegradation
  expr: model_top1_accuracy < 0.8
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Dégradation de l'accuracy Top-1"
    description: "L'accuracy Top-1 est tombée en dessous de 80%"
    dashboard: "http://localhost:3001/d/engravedetect-dashboard"
```

---

## Scripts de Test

### 1. `scripts/generate_test_data.py`
**Objectif** : Générer des données de test pour les métriques

**Utilisation** :
```bash
python3 scripts/generate_test_data.py
```

**Fonctionnalités** :
- Authentification automatique
- Recherche d'images de test
- Génération de 10 requêtes avec pauses
- Gestion du rate limiting

### 2. `scripts/test_drift_detection.py`
**Objectif** : Tester la détection de drift avec des images diverses

**Utilisation** :
```bash
python3 scripts/test_drift_detection.py
```

**Fonctionnalités** :
- Utilisation d'images de classes différentes
- 30 images × 3 cycles = 90 requêtes
- Maximisation des chances de détecter du drift

### 3. `scripts/debug_drift.py`
**Objectif** : Debug de la détection de drift

**Utilisation** :
```bash
python3 scripts/debug_drift.py
```

**Fonctionnalités** :
- Vérification des métriques avant/après
- Test de la santé du modèle
- Diagnostic des problèmes de drift

---

## Procédures d'Opération

### 1. Vérification de l'état du monitoring
```bash
# Vérifier que Prometheus collecte les métriques
curl http://localhost:9090/api/v1/targets

# Vérifier les métriques de l'API IA
curl http://localhost:8001/metrics | grep model_

# Vérifier la santé du modèle
curl http://localhost:8001/model/health | jq
```

### 2. Diagnostic des problèmes
```bash
# Vérifier les logs de l'API IA
docker compose logs api_ia

# Vérifier les logs de Prometheus
docker compose logs prometheus

# Vérifier les logs de Grafana
docker compose logs grafana
```

### 3. Test du monitoring
```bash
# Générer des données de test
python3 scripts/generate_test_data.py

# Vérifier l'apparition des métriques
curl http://localhost:8001/metrics | grep model_drift_score
```

---

## Maintenance

### 1. Sauvegarde des dashboards
```bash
# Exporter le dashboard Grafana
curl -H "Authorization: Bearer $GRAFANA_TOKEN" \
  http://localhost:3001/api/dashboards/uid/engravedetect > dashboard_backup.json
```

### 2. Mise à jour des seuils
- Modifier `monitoring/grafana/engravedetect_dashboard.json`
- Modifier `monitoring/prometheus/model_alerts.yml`
- Redémarrer les services

### 3. Nettoyage des données
- Prometheus : Rétention configurable dans `prometheus.yml`
- Logs : Rotation automatique via Docker

---

## Conclusion

Le monitoring de l'API IA EngraveDetect offre une visibilité complète sur les performances du modèle, la qualité des prédictions et la détection de dérives. L'architecture Prometheus/Grafana permet une surveillance en temps réel et des alertes proactives pour maintenir la qualité du service.

Les métriques exposées couvrent tous les aspects critiques : performance, qualité, drift et santé du système. Les scripts de test facilitent la validation du monitoring et la génération de données de test. 