# Tests d'intégration API IA - Documentation simplifiée

## Vue d'ensemble

Tests d'intégration essentiels pour l'API IA du projet EngraveDetect.
Tests simples et efficaces pour vérifier le bon fonctionnement des endpoints principaux.

## Tests disponibles

### Endpoints testés

1. **`/token`** - Authentification JWT
2. **`/embedding`** - Génération d'embeddings d'images
3. **`/match`** - Recherche de correspondances de classes
4. **`/search_tags`** - Recherche de verres par tags
5. **`/health`** - Santé de l'API

### Fonctionnalités testées

- Authentification et autorisation
- Validation des données d'entrée
- Réponses et codes de statut
- Gestion des erreurs basiques

## Exécution des tests

```bash
# Exécuter les tests d'intégration API IA
pytest tests/test_routes/test_api_ia_integration.py -v

# Avec couverture de code
pytest --cov=api_ia tests/test_routes/test_api_ia_integration.py -v
```

## Structure des tests

### TestAPIIAIntegration

- `test_token_endpoint()` - Vérifie l'authentification
- `test_embedding_endpoint()` - Vérifie la génération d'embeddings
- `test_match_endpoint()` - Vérifie la recherche de correspondances
- `test_search_tags_endpoint()` - Vérifie la recherche par tags
- `test_health_check()` - Vérifie la santé de l'API
- `test_authentication_required()` - Vérifie que l'auth est requise
- `test_invalid_image_rejected()` - Vérifie le rejet des fichiers invalides

## Mocks utilisés

Les tests utilisent des mocks simples pour :
- Authentification (`api_ia.app.security.authenticate_user`)
- Génération d'embeddings (`api_ia.app.model_loader.get_embedding`)
- Recherche de correspondances (`api_ia.app.similarity_search.get_top_matches`)
- Recherche par tags (`api_ia.app.database.find_matching_verres`)

## Cas de test

### Authentification
- ✅ Identifiants valides → Token JWT retourné
- ❌ Requête sans token → 401 Unauthorized

### Endpoint /embedding
- ✅ Image valide + token → Embedding 512 dimensions
- ❌ Fichier non-image → 400 Bad Request

### Endpoint /match
- ✅ Image valide + token → Liste de correspondances
- ✅ Structure de réponse correcte (class_, similarity)

### Endpoint /search_tags
- ✅ Tags valides + token → Liste de verres correspondants

## Maintenance

### Ajouter un nouveau test

1. Identifier l'endpoint à tester
2. Créer une méthode `test_nom_endpoint()`
3. Ajouter les mocks nécessaires
4. Vérifier le code de statut et la structure de réponse

### Exemple

```python
def test_nouveau_endpoint(self, client, auth_token):
    """Test du nouvel endpoint"""
    with patch('api_ia.app.module.fonction') as mock_fonction:
        mock_fonction.return_value = {"result": "test"}
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post("/nouveau", json={}, headers=headers)
        
        assert response.status_code == 200
        assert "result" in response.json()
```

## Conclusion

Tests simples, efficaces et maintenables pour vérifier le bon fonctionnement de l'API IA. 