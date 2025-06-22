
# README — Tests automatisés IA pour EngraveDetect

Ce fichier a pour but de documenter les tests automatisés mis en place autour du modèle d’intelligence artificielle du projet EngraveDetect, dans le cadre du critère **C12 du bloc E3** de la certification RNCP 37638.

---

## 🧪 Objectifs

Les tests permettent de garantir que :

- les composants critiques (modèle, API IA, services métiers) fonctionnent comme attendu ;
- chaque modification future pourra être validée automatiquement ;
- le comportement de l’IA est conforme aux spécifications techniques du projet.

---

## ✅ Cas testés

Voici les cas de test couverts par les différents scripts présents dans le dépôt :

| Script | Cible testée | Périmètre | Description |
|--------|---------------|-----------|-------------|
| `test_model.py` | Modèle TripletNet | Structure et forward pass | Vérifie la compatibilité du modèle avec PyTorch, la forme de sortie |
| `test_evaluate_model.py` | Fonction d’évaluation | Embeddings, top-k accuracy | Évalue les performances sur des embeddings simulés |
| `test_verres_services.py` | Services métiers | Matching, extraction de tags | Teste les fonctions de recherche de verres et tags |
| `test_main.py` | API IA | Endpoints REST | Teste `/embedding`, `/match`, `/search_tags`, `/verre/{id}` |
| `conftest.py` | Données simulées | Fixtures de test | Génère des images de test et jeux simulés pour pytest |

---

## ⚙️ Environnement technique

- Langage : Python 3.10+
- Tests : `pytest`
- API testée : FastAPI (`TestClient`)
- Isolation : Docker (conteneur `api_ia`)

---

## 📦 Dépendances requises

Les dépendances sont gérées automatiquement dans l’image Docker. Pour référence :

```txt
pytest
fastapi
python-multipart
torch
numpy
scikit-learn
```

---

## 🚀 Exécution des tests

Depuis la racine du projet, lancer :

```bash
docker compose exec api_ia pytest -v
```

Tous les fichiers de test se trouvent dans le répertoire `/tests`.

---

## 📊 Calcul de couverture (optionnel)

Pour mesurer la couverture, il est recommandé d’ajouter :

```bash
pip install pytest-cov
pytest --cov=src/api_ia
```

(à intégrer dans un futur pipeline CI/CD)

---

## 🔐 Versionnage et sécurité

Les tests sont présents dans le dépôt Git du projet.  
Aucune donnée sensible n’est versionnée (usage de `.env` pour les secrets).

---

## ♿ Accessibilité

Ce fichier est fourni au format Markdown, lisible par tous les lecteurs d’écran. Il respecte les recommandations d’accessibilité de l’association Valentin Haüy.

---

## 📁 Structure concernée

```
tests/
├── conftest.py
├── test_model.py
├── test_main.py
├── test_evaluate_model.py
└── test_verres_services.py
```

---

