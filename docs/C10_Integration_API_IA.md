# C10. Intégration de l'API d'Intelligence Artificielle

## Contexte et Objectifs

L’intégration de l’API IA dans EngraveDetect permet l’analyse et la classification d’images de verres optiques via un modèle PyTorch EfficientNet, accessible par une API FastAPI dédiée, sécurisée et conforme RGPD.

## Environnement de Développement

- **API IA** : Port 8001 (`src/api_ia/`)
- **API Principale** : Port 8000 (`src/api/`)
- **Base de données** : Azure SQL (paramétrage dans `.env` et `src/api_ia/app/config.py`)

### Structure du Projet

```
src/
├── api/           # API principale (gestion utilisateurs, verres, auth)
├── api_ia/        # API IA (classification, embeddings, recherche)
└── front/         # Interface utilisateur
```

## Communication avec l’API IA

### Authentification

- **/token** (POST) : Authentification OAuth2 (JWT)
  - Reçoit : `username`, `password` (form-data)
  - Retourne : `{ "access_token": "...", "token_type": "bearer", "version": "1" }`
- **JWT** : Obligatoire pour tous les endpoints IA sauf `/token`, `/`, `/health`, `/metrics`
- **Vérification** : Décodage, expiration, validation en base, logs de sécurité

### Endpoints Principaux

#### 1. **/embedding** (POST)
- Authentification : Obligatoire (Bearer)
- Paramètres : `file` (UploadFile, image JPG/PNG)
- Limite : 5 requêtes/minute (SlowAPI)
- Réponse : `{ "embedding": [float, ...] }`
- Erreurs : 400 (image invalide), 401 (auth), 500 (erreur interne)

#### 2. **/match** (POST)
- Authentification : Obligatoire (Bearer)
- Paramètres : `file` (UploadFile, image JPG/PNG)
- Limite : 5 requêtes/minute
- Réponse : `{ "matches": [ { "class": "nom_classe", "similarity": 0.95 }, ... ] }`
- Fonctionnement : Extraction embedding, recherche des 20 plus proches via similarité cosinus sur embeddings de référence
- Erreurs : 400, 401, 500

#### 3. **/search_tags** (POST)
- Authentification : Obligatoire (Bearer)
- Paramètres : `tags` (body JSON, liste de chaînes)
- Limite : 10 requêtes/minute
- Réponse : `{ "results": [ { "id": ..., "nom": ..., "tags": [...], ... }, ... ] }`
- Fonctionnement : Recherche de verres contenant au moins un des tags

#### 4. **/verre/{id}** (GET)
- Authentification : Obligatoire (Bearer)
- Paramètres : `id` (int, path)
- Limite : 20 requêtes/minute
- Réponse : `{ "verre": { ... } }` ou `{ "error": "Verre non trouvé" }`

#### 5. **/me** (GET, DELETE)
- Authentification : Obligatoire (Bearer)
- GET : Retourne `{ "username": ..., "email": ... }` (données RGPD)
- DELETE : Supprime le compte utilisateur (droit à l’oubli RGPD)

#### 6. **Endpoints publics**
- `/` (GET) : Message d’accueil
- `/health` (GET) : Statut de santé
- `/metrics` (GET) : Statistiques Prometheus

### Sécurité

- **Validation stricte** des fichiers images (taille, type MIME, signature)
- **Logs de sécurité** (création/suppression de comptes, tokens, erreurs)
- **Rate limiting** sur tous les endpoints critiques
- **JWT** : Expiration, vérification, logs d’événements

## Tests d’Intégration

### Couverture réelle

- **tests/test_main.py** : Teste la route racine de l’API principale (pas l’API IA)
- **tests/README_TESTS.md** : Documente la structure des tests IA (voir ci-dessous)
- **tests/test_performance.py** : Placeholders pour tests de performance IA/API/DB (non implémentés)
- **tests/test_services/test_verres_services.py** : Teste la logique métier des verres (API principale)
- **tests/test_evaluate_model.py, test_model.py** : Testent le modèle et les embeddings (unitaires, pas d’intégration API IA)

**À ce jour, il n’existe pas de tests automatisés d’intégration pour les endpoints de l’API IA dans le dépôt.**  
La documentation antérieure mentionnait des tests sur `/embedding`, `/match`, `/search_tags`, `/verre/{id}` mais ils ne sont pas présents dans le code.

### À faire pour une couverture complète

- Ajouter des tests d’intégration pour chaque endpoint IA : upload image, auth, RGPD, erreurs
- Implémenter les tests de performance (temps de réponse, charge)
- Ajouter des tests d’erreur et de sécurité (fichiers invalides, tokens expirés, etc.)

## Versioning

- **Branche `main`** : Production
- **Branches `feature/*`** : Développement

## Points à Améliorer

1. **Tests**
   - Ajouter des tests d’intégration réels pour l’API IA
   - Implémenter les tests de performance
2. **Sécurité**
   - Continuer à renforcer la validation des entrées et la gestion des erreurs
   - Auditer les logs de sécurité
3. **Documentation**
   - Ajouter des exemples d’utilisation réels (curl, Python, etc.)
   - Documenter les cas d’erreur et les réponses attendues

## Conclusion

L’API IA EngraveDetect est modulaire, sécurisée, conforme RGPD, et expose des endpoints robustes pour l’analyse d’images.  
La couverture de tests d’intégration doit être renforcée pour garantir la fiabilité en production.

---

