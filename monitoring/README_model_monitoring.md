# Monitoring du Modèle d'IA - EngraveDetect

Ce document décrit la chaîne de monitoring spécifique au **modèle d'IA** EngraveDetect, distincte du monitoring de l'API. Cette implémentation répond aux exigences RNCP C11 pour le monitoring d'un modèle d'intelligence artificielle.

---

##  Métriques du Modèle d'IA

### **Métriques de Performance**
- **`model_accuracy`** : Accuracy du modèle basée sur les scores de confiance (> 0.8 = succès)
- **`model_inference_time_seconds`** : Temps d'inférence du modèle (latence)
- **`model_predictions_total`** : Nombre total de prédictions effectuées
- **`model_predictions_success`** : Nombre de prédictions réussies
- **`model_predictions_failed`** : Nombre de prédictions échouées

### **Métriques de Qualité**
- **`model_prediction_confidence`** : Distribution des scores de confiance des prédictions
- **`model_embedding_quality`** : Qualité des embeddings générés (basée sur l'écart-type)

### **Métriques de Drift**
- **`model_drift_score`** : Score de détection de drift des données d'entrée (0-1)

---

##  Outils de Monitoring

### **Collecte de Données**

- **Prometheus** : Collecte et stockage des métriques
- **Instrumentation native** : Intégrée dans l'API FastAPI

### **Visualisation et Restitution**
- **Grafana** : Dashboard temps réel pour les métriques du modèle
- **Prometheus UI** : Interface de requête des métriques
- **Endpoint `/model/health`** : API REST pour le statut du modèle

### **Alertes**
- **Prometheus AlertManager** : Système d'alertes automatiques
- **Seuils configurables** : Alertes sur dégradation, drift, latence

---

##  Dashboard Grafana

### **Accès**
- **URL** : `http://localhost:3001`
- **Dashboard** : "Modèle IA - Monitoring EngraveDetect"
- **Rafraîchissement** : 30 secondes

### **Panels Disponibles**
1. **Performance du Modèle** : Accuracy en temps réel
2. **Temps d'Inférence** : Latence moyenne du modèle
3. **Distribution des Scores** : Histogramme des confiances
4. **Détection de Drift** : Gauge du score de drift
5. **Qualité des Embeddings** : Métrique de qualité
6. **Volume de Prédictions** : Débit des prédictions
7. **Taux de Réussite** : Pourcentage de succès
8. **Évolution Temporelle** : Graphique d'évolution des métriques

---

##  Système d'Alertes

### **Alertes Configurées**
- **Dégradation d'Accuracy** : < 85% pendant 5 minutes
- **Drift Détecté** : Score > 0.7 pendant 2 minutes
- **Latence Élevée** : > 2 secondes (95e percentile)
- **Qualité Dégradée** : < 50% pendant 5 minutes
- **Taux d'Échec** : > 10% pendant 2 minutes
- **Aucune Prédiction** : 0 prédiction pendant 10 minutes

### **Niveaux de Sévérité**
- **Warning** : Dégradation modérée, surveillance requise
- **Critical** : Problème grave, action immédiate nécessaire

---

##  Accessibilité

### **Conformité WCAG 2.1 AA**
- **Contrastes** : Respect des ratios de contraste (4.5:1 minimum)
- **Navigation clavier** : Interface entièrement navigable au clavier
- **Lecteurs d'écran** : Compatible avec les technologies d'assistance
- **Textes alternatifs** : Descriptions pour tous les éléments visuels

### **Parties Prenantes**
- **Équipe technique** : Dashboard détaillé avec métriques avancées
- **Opticien** : Interface simplifiée avec alertes visuelles
- **Encadrant** : Vue d'ensemble avec indicateurs clés

---

##  Tests en Bac à Sable

### **Environnement de Test**
- **Docker Compose** : Environnement isolé et reproductible
- **Données de test** : Jeu de données contrôlé pour validation
- **Scénarios de test** : Drift simulé, dégradation de performance

### **Validation**
-  **Métriques collectées** : Vérification de la collecte
-  **Alertes déclenchées** : Test des seuils d'alerte
-  **Dashboard fonctionnel** : Validation de l'affichage
-  **Performance** : Impact négligeable sur l'API

---

##  Architecture des Fichiers

```
monitoring/
├── prometheus/
│   ├── prometheus.yml          # Configuration Prometheus
│   └── model_alerts.yml        # Règles d'alertes du modèle
├── grafana/
│   ├── fastapi_monitoring.json # Dashboard API (existant)
│   └── model_monitoring_dashboard.json # Dashboard modèle (nouveau)
└── README_model_monitoring.md  # Cette documentation

src/api_ia/app/
├── main.py                     # API avec monitoring intégré
└── model_monitoring.py         # Module de monitoring du modèle
```

---

##  Installation et Démarrage

### **1. Installation des Dépendances**
```bash

```

### **2. Démarrage de la Chaîne**
```bash
docker compose up --build
```

### **3. Accès aux Interfaces**
- **API IA** : `http://localhost:8001`
- **Prometheus** : `http://localhost:9090`
- **Grafana** : `http://localhost:3001`
- **Statut modèle** : `http://localhost:8001/model/health`

---

##  Utilisation en Production

### **Surveillance Continue**
1. **Dashboard Grafana** : Surveillance visuelle en temps réel
2. **Alertes Prometheus** : Notifications automatiques
3. **Endpoint `/model/health`** : Vérification programmatique
4. **Logs** : Traçabilité complète des événements

### **Maintenance**
- **Mise à jour des seuils** : Ajustement selon l'évolution du modèle
- **Ajout de métriques** : Extension du monitoring selon les besoins
- **Optimisation** : Ajustement de la fréquence de détection de drift

---

##  Validation RNCP C11

Cette implémentation répond point par point aux exigences :

1.  **Métriques expliquées** : Documentation complète de chaque métrique
2.  **Outils adaptés** : Prometheus + Grafana + Détection de drift personnalisée
3.  **Restitution temps réel** : Dashboard Grafana avec rafraîchissement 30s
4.  **Accessibilité** : Conformité WCAG 2.1 AA
5.  **Test en bac à sable** : Environnement Docker isolé
6.  **Chaîne fonctionnelle** : Métriques collectées et restituées
7.  **Sources versionnées** : Code dans le dépôt Git
8.  **Documentation technique** : Ce document + commentaires code

---

##  Configuration Avancée

### **Ajustement des Seuils**
```python
# Dans src/api_ia/app/model_monitoring.py
class ModelMonitor:
    def __init__(self, embedding_dim: int = 128):
        self.confidence_threshold = 0.8  # Seuil de confiance
        self.drift_detection_frequency = 0.1  # Fréquence de détection
```

### **Personnalisation des Alertes**
```yaml
# Dans monitoring/prometheus/model_alerts.yml
- alert: ModelAccuracyDegradation
  expr: model_accuracy < 0.85  # Seuil personnalisable
  for: 5m
```

---

##  Support

Pour toute question sur le monitoring du modèle d'IA :
- **Documentation** : Ce fichier README
- **Code source** : `src/api_ia/app/model_monitoring.py`
- **Configuration** : Fichiers dans `monitoring/`
- **Logs** : Console de l'API IA 