# Monitoring du modèle IA — EngraveDetect

Ce document décrit la mise en place de la chaîne de monitoring utilisée pour superviser l’API IA du projet EngraveDetect. Cette chaîne repose sur l'intégration de **Prometheus** pour la collecte des métriques, et **Grafana** pour leur visualisation en temps réel.

---

## 📦 Installation

La chaîne complète est incluse dans le `docker-compose.yml` à la racine du projet.  
Elle se lance automatiquement en même temps que l’API IA et les autres services :

```bash
docker compose up --build
```

Les services suivants sont démarrés :

- `prometheus` (port : `9090`)
- `grafana` (port : `3001`)
- `api_ia` (port : `8001`), exposant la route `/metrics`

---

## ⚙️ Configuration

### 🔎 Prometheus

Le fichier `prometheus/prometheus.yml` définit les endpoints à scrapper. L’API IA expose automatiquement les métriques à l’URL suivante :

```
http://api_ia:8000/metrics
```

Ce endpoint est généré via le middleware :

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 📈 Grafana

Grafana est préconfiguré pour lire les données exposées par Prometheus.  
Le port `3001` permet d’accéder à l’interface :

```
http://localhost:3001
```

---

## 📊 Métriques surveillées

Les métriques disponibles sont les suivantes :

- `http_server_requests_seconds_count` : nombre de requêtes traitées par endpoint
- `http_server_requests_seconds_sum` : latence agrégée par route
- `http_server_requests_exceptions_total` : erreurs serveur
- `http_requests_total` : nombre total de requêtes reçues
- `uptime_seconds` : durée de fonctionnement de l’API

Ces métriques permettent de :

- Détecter une dégradation de performance (ex. hausse de latence sur `/match`)
- Surveiller la stabilité (nombre d’erreurs)
- Vérifier le bon fonctionnement global du modèle en production

---

## ♿ Accessibilité et parties prenantes

Le choix de Grafana s’est appuyé sur sa conformité avec les recommandations **WCAG 2.1 niveau AA**, avec :

- Une interface **navigable au clavier**
- Des contrastes lisibles
- La possibilité d’ajouter des **commentaires lisibles à l’écran**
- Un affichage clair pour les personnes non techniques (opticiens, encadrants)

L’interface de monitoring est pensée pour pouvoir être montrée en réunion ou partagée avec un lien sécurisé aux parties prenantes.

---

## 🧪 Tests en environnement isolé

La chaîne de monitoring a été déployée et testée en **bac à sable local** via Docker.  
Aucun impact n’a été constaté sur la performance de l’API IA en conditions normales.

---

## 📁 Fichiers concernés

```
.
├── prometheus/
│   └── prometheus.yml
├── docker-compose.yml
├── src/
│   └── api_ia/
│       └── app/
│           └── main.py (Instrumentation Prometheus)
```

---



---

## ✅ Validation des critères RNCP (C11)

Cette chaîne de monitoring répond point par point aux exigences du critère **C11 : Monitorer un modèle d’intelligence artificielle** :

1. **Métriques expliquées sans erreur d’interprétation** :  
   → Les métriques Prometheus sont décrites dans la section *Métriques surveillées* ci-dessus.

2. **Outils adaptés au projet** :  
   → L’intégration de Prometheus et Grafana est compatible avec l’environnement Dockerisé et la stack Python/FastAPI déjà en place.

3. **Restitution en temps réel** :  
   → Grafana fournit un dashboard consultable en direct sur le port 3001.

4. **Accessibilité prise en compte** :  
   → Grafana respecte les standards WCAG 2.1 AA, l’interface est lisible, contrastée et utilisable au clavier.

5. **Test en bac à sable** :  
   → L’environnement Docker assure un déploiement isolé sans risque, utilisé pour tester la chaîne.

6. **Chaîne fonctionnelle** :  
   → Prometheus scrap correctement `/metrics` et Grafana affiche les données. La chaîne est en production localisée.

7. **Sources versionnées** :  
   → Tous les fichiers de configuration sont présents dans le dépôt Git (`prometheus/`, `docker-compose.yml`, etc.)

8. **Documentation technique complète** :  
   → Ce présent fichier sert de documentation technique. Il couvre l’installation, l’usage, la configuration, la structure, et les bonnes pratiques.

9. **Format accessible** :  
   → La documentation est fournie en Markdown lisible par un lecteur d’écran ou tout éditeur de texte compatible avec les recommandations de Microsoft ou de l’association Valentin Haüy.