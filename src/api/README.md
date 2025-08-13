#  API EngraveDetect

API REST pour la gestion et l'analyse des verres optiques, développée avec FastAPI.

##  Fonctionnalités

-  Recherche et filtrage des verres
-  Statistiques et analyses
-  Authentification JWT
-  Documentation OpenAPI/Swagger
-  Validation des données avec Pydantic
-  Gestion des erreurs standardisée

##  Structure

```
api/
├── core/           # Configuration et utilitaires
├── models/         # Modèles SQLAlchemy
├── routes/         # Routes API
├── schemas/        # Schémas Pydantic
└── services/       # Logique métier
```

##  Démarrage

1. **Installation des dépendances**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos paramètres
   ```

3. **Lancer le serveur**
   ```bash
   uvicorn src.api.main:app --reload
   ```

##  Endpoints Principaux

### Verres
- `GET /api/v1/verres` - Liste des verres
- `GET /api/v1/verres/{id}` - Détails d'un verre
- `POST /api/v1/verres` - Créer un verre
- `PUT /api/v1/verres/{id}` - Mettre à jour un verre
- `DELETE /api/v1/verres/{id}` - Supprimer un verre

### Statistiques
- `GET /api/v1/stats/fournisseurs` - Stats par fournisseur
- `GET /api/v1/stats/materiaux` - Stats par matériau
- `GET /api/v1/stats/gammes` - Stats par gamme

### Authentification
- `POST /api/v1/auth/token` - Obtenir un token
- `POST /api/v1/auth/refresh` - Rafraîchir un token

##  Sécurité

- Authentification JWT
- Validation des entrées
- Protection CSRF
- Rate limiting
- Logging des accès

##  Tests

```bash
# Tests de l'API
pytest tests/api/

# Tests avec couverture
pytest --cov=src.api tests/api/
```

##  Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

##  Workflow de Développement

1. Créer une branche pour la fonctionnalité
2. Implémenter les tests
3. Développer la fonctionnalité
4. Vérifier les tests
5. Créer une PR

##  Débogage

- Logs détaillés dans `logs/api.log`
- Mode debug avec `--debug`
- Traces d'erreurs complètes

##  Monitoring

- Métriques Prometheus
- Health checks
- Performance monitoring 