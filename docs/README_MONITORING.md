# Monitoring EngraveDetect - Guide Complet

Ce guide explique comment configurer, utiliser et maintenir le système de monitoring d'EngraveDetect avec Grafana et Prometheus.

##  Architecture du Monitoring

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API IA        │    │   Prometheus    │    │   Grafana       │
│   (Port 8001)   │───▶│   (Port 9090)   │───▶│   (Port 3001)   │
│                 │    │                 │    │                 │
│ - Métriques     │    │ - Collecte      │    │ - Dashboards    │
│ - Endpoint      │    │ - Stockage      │    │ - Visualisation │
│   /metrics      │    │ - Alertes       │    │ - Alertes       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

##  Lancement avec Docker Compose

### 1. Démarrage rapide

```bash
# Lancer tous les services
docker-compose up -d

# Vérifier que les services sont démarrés
docker-compose ps
```

### 2. Accès aux services

- **Application principale** : http://37.27.217.233:8080/
- **Grafana** : http://37.27.217.233:3001/
- **Prometheus** : http://37.27.217.233:9090/
- **API IA** : http://37.27.217.233:8001/

### 3. Configuration des services

#### Grafana
- **Utilisateur admin** : Variable d'environnement `GF_SECURITY_ADMIN_USER`
- **Mot de passe** : Variable d'environnement `GF_SECURITY_ADMIN_PASSWORD`
- **Configuration** : `monitoring/grafana/grafana.ini`

#### Prometheus
- **Configuration** : `monitoring/prometheus/prometheus.yml`
- **Règles d'alertes** : `monitoring/prometheus/rules/`

##  Métriques Collectées

### Métriques de Performance du Modèle

| Métrique | Type | Description |
|----------|------|-------------|
| `model_top1_accuracy` | Gauge | Précision Top-1 du modèle |
| `model_top3_accuracy` | Gauge | Précision Top-3 du modèle |
| `model_inference_time_seconds` | Histogram | Temps d'inférence |
| `model_prediction_confidence` | Histogram | Confiance des prédictions |

### Métriques de Qualité

| Métrique | Type | Description |
|----------|------|-------------|
| `model_embedding_quality` | Gauge | Qualité des embeddings |
| `model_embedding_normality` | Gauge | Normalité des embeddings |
| `model_feature_activation` | Gauge | Activation des features |

### Métriques de Volume

| Métrique | Type | Description |
|----------|------|-------------|
| `model_predictions_total` | Counter | Total des prédictions |
| `model_predictions_success` | Counter | Prédictions réussies |
| `model_predictions_failed` | Counter | Prédictions échouées |

### Métriques de Drift

| Métrique | Type | Description |
|----------|------|-------------|
| `model_drift_score` | Gauge | Score de drift des données |

##  Où modifier les métriques

### Fichier principal : `src/api_ia/app/model_monitoring.py`

Ce fichier contient la classe `ModelMonitor` qui gère toutes les métriques :

```python
class ModelMonitor:
    def __init__(self):
        # Définition des métriques Prometheus
        self.model_top1_accuracy = Gauge(
            "model_top1_accuracy", 
            "Top-1 accuracy du modèle", 
            ["model_name"]
        )
        # ... autres métriques
```

### Utilisation dans le code : `src/api_ia/app/main.py`

```python
# Mise à jour des métriques lors d'une prédiction
model_monitor.update_prediction_metrics(
    embedding=embedding,
    similarity_scores=similarity_scores,
    inference_time=inference_time,
    success=True
)
```

##  Comment ajouter une nouvelle métrique

### Étape 1 : Définir la métrique dans `model_monitoring.py`

```python
class ModelMonitor:
    def __init__(self):
        # Nouvelle métrique
        self.model_custom_metric = Counter(
            "model_custom_metric",
            "Description de la nouvelle métrique",
            ["model_name", "label1", "label2"]
        )
```

### Étape 2 : Mettre à jour la métrique dans le code

```python
def update_prediction_metrics(self, ...):
    # Mise à jour de la nouvelle métrique
    self.model_custom_metric.labels(
        self.model_name, 
        "value1", 
        "value2"
    ).inc()
```

### Étape 3 : Ajouter au dashboard Grafana

1. Ouvrir Grafana : http://37.27.217.233:3001/
2. Aller dans le dashboard "EngraveDetect - Monitoring Modèle IA"
3. Cliquer sur "Add panel"
4. Configurer la requête Prometheus : `model_custom_metric`

### Exemple complet : Ajout d'une métrique de latence

```python
# 1. Dans model_monitoring.py
self.model_latency_p95 = Histogram(
    "model_latency_p95",
    "95ème percentile de latence",
    ["model_name"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# 2. Mise à jour dans update_prediction_metrics
self.model_latency_p95.labels(self.model_name).observe(inference_time)

# 3. Requête Prometheus pour le dashboard
histogram_quantile(0.95, rate(model_latency_p95_bucket[5m]))
```

##  Dashboards Grafana

### Dashboard principal : "EngraveDetect - Monitoring Modèle IA"

**Fichier** : `monitoring/grafana/engravedetect_dashboard.json`

**URL d'accès** : http://37.27.217.233:3001/d/engravedetect/engravedetect-monitoring-modele-ia

### Panels disponibles

1. **Accuracy Metrics**
   - Top-1 Accuracy (Gauge)
   - Top-3 Accuracy (Gauge)

2. **Performance Metrics**
   - Inference Time (Histogram)
   - Throughput (Gauge)

3. **Quality Metrics**
   - Embedding Quality (Gauge)
   - Prediction Confidence (Histogram)

4. **Volume Metrics**
   - Total Predictions (Counter)
   - Success/Failure Rate (Counter)

### Comment modifier le dashboard

#### Option 1 : Via l'interface Grafana (Recommandé)

1. **Accéder au dashboard** : http://37.27.217.233:3001/
2. **Se connecter** avec les identifiants admin
3. **Modifier le panel** :
   - Cliquer sur le titre du panel
   - Sélectionner "Edit"
   - Modifier la requête Prometheus
   - Sauvegarder

#### Option 2 : Modifier le fichier JSON

1. **Éditer** : `monitoring/grafana/engravedetect_dashboard.json`
2. **Ajouter un nouveau panel** :

```json
{
  "id": 999,
  "title": "Nouveau Panel",
  "type": "graph",
  "targets": [
    {
      "expr": "votre_requete_prometheus",
      "refId": "A"
    }
  ],
  "gridPos": {
    "x": 0,
    "y": 0,
    "w": 12,
    "h": 8
  }
}
```

3. **Redéployer** : `docker-compose restart grafana`

### Exemple : Ajout d'un panel de métrique personnalisée

```json
{
  "id": 100,
  "title": "Métrique Personnalisée",
  "type": "stat",
  "datasource": {
    "type": "prometheus",
    "uid": "prometheus"
  },
  "gridPos": {
    "x": 0,
    "y": 0,
    "w": 6,
    "h": 4
  },
  "targets": [
    {
      "expr": "model_custom_metric_total",
      "refId": "A"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "color": {
        "mode": "thresholds"
      },
      "thresholds": {
        "steps": [
          {"color": "green", "value": null},
          {"color": "red", "value": 100}
        ]
      }
    }
  }
}
```

##  Requêtes Prometheus utiles

### Métriques de base

```promql
# Taux de succès des prédictions
rate(model_predictions_success_total[5m]) / rate(model_predictions_total_total[5m])

# Temps d'inférence moyen
rate(model_inference_time_seconds_sum[5m]) / rate(model_inference_time_seconds_count[5m])

# 95ème percentile de latence
histogram_quantile(0.95, rate(model_inference_time_seconds_bucket[5m]))

# Drift score actuel
model_drift_score
```

### Alertes recommandées

```yaml
# Règle d'alerte pour drift élevé
- alert: HighDataDrift
  expr: model_drift_score > 0.8
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Drift de données élevé détecté"
    description: "Le score de drift est {{ $value }}"

# Règle d'alerte pour latence élevée
- alert: HighInferenceLatency
  expr: histogram_quantile(0.95, rate(model_inference_time_seconds_bucket[5m])) > 2
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Latence d'inférence élevée"
    description: "95ème percentile: {{ $value }}s"
```

##  Maintenance et Dépannage

### Vérifier l'état des services

```bash
# État des conteneurs
docker-compose ps

# Logs des services
docker-compose logs grafana
docker-compose logs prometheus
docker-compose logs api_ia

# Vérifier les métriques
curl http://37.27.217.233:8001/metrics
```

### Problèmes courants

#### 1. Métriques non visibles dans Grafana
- Vérifier que Prometheus collecte les métriques : http://37.27.217.233:9090/targets
- Vérifier la configuration Prometheus : `monitoring/prometheus/prometheus.yml`

#### 2. Dashboard ne se charge pas
- Vérifier les permissions Grafana
- Redémarrer le conteneur : `docker-compose restart grafana`

#### 3. Métriques non mises à jour
- Vérifier les logs de l'API IA : `docker-compose logs api_ia`
- Vérifier que l'endpoint `/metrics` répond

### Sauvegarde et restauration

```bash
# Sauvegarder les dashboards
docker exec grafana grafana-cli admin backup

# Sauvegarder les données Prometheus
docker exec prometheus promtool tsdb backup /prometheus/data

# Restaurer
docker exec grafana grafana-cli admin restore backup.tar.gz
```

##  Ressources supplémentaires

- [Documentation Prometheus](https://prometheus.io/docs/)
- [Documentation Grafana](https://grafana.com/docs/)
- [Guide des métriques Prometheus](https://prometheus.io/docs/concepts/metric_types/)
- [Requêtes PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/)

##  Liens utiles

- **Dashboard principal** : http://37.27.217.233:3001/d/engravedetect/engravedetect-monitoring-modele-ia
- **Grafana** : http://37.27.217.233:3001/
- **Prometheus** : http://37.27.217.233:9090/
- **Métriques brutes** : http://37.27.217.233:8001/metrics 