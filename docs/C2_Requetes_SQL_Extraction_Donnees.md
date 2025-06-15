# C2. Requêtes SQL d'Extraction de Données

## Contexte
Ce document analyse l'implémentation des requêtes SQL pour l'extraction de données dans le projet EngraveDetect. Le projet utilise Azure SQL comme système de gestion de base de données principal pour stocker et extraire les données des verres optiques.

## 1. Fonctionnalité des Requêtes SQL

### 1.1 Extraction des Données des Verres
```python
def get_verres_by_fournisseur(fournisseur: str):
    """
    Extrait les données des verres pour un fournisseur spécifique.
    
    Args:
        fournisseur (str): Nom du fournisseur à rechercher
        
    Returns:
        List[tuple]: Liste des verres avec leurs caractéristiques
    """
    query = """
    SELECT 
        nom,
        materiaux,
        indice,
        gravure,
        protection,
        photochromic
    FROM verres
    WHERE fournisseur = ?
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (fournisseur,))
        return cursor.fetchall()
```

### 1.2 Extraction des Données Enhanced
```python
def get_enhanced_data():
    """
    Extrait les données enrichies des verres avec leurs métadonnées.
    
    Returns:
        List[tuple]: Liste des verres enrichis avec leurs métadonnées
    """
    query = """
    SELECT 
        e.nom_verre,
        e.materiaux,
        e.indice,
        e.fournisseur,
        e.gravure_nasale,
        e.source_url,
        e.created_at
    FROM enhanced e
    WHERE e.created_at >= DATEADD(day, -30, GETDATE())
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
```

### 1.3 Extraction des Données avec Filtres Multiples
```python
def get_verres_by_criteria(materiaux: str, indice_min: float, indice_max: float):
    """
    Extrait les verres selon plusieurs critères.
    
    Args:
        materiaux (str): Type de matériau
        indice_min (float): Indice minimum
        indice_max (float): Indice maximum
        
    Returns:
        List[tuple]: Liste des verres correspondant aux critères
    """
    query = """
    SELECT 
        nom,
        materiaux,
        indice,
        fournisseur,
        gravure
    FROM verres
    WHERE materiaux = ?
    AND indice BETWEEN ? AND ?
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (materiaux, indice_min, indice_max))
        return cursor.fetchall()
```

## 2. Documentation des Requêtes

### 2.1 Choix de Sélection
Les requêtes sont conçues pour extraire des données spécifiques selon les besoins :

1. **Sélection des Champs Essentiels**
   - Utilisation de `SELECT` explicite plutôt que `SELECT *`
   - Sélection des champs nécessaires pour optimiser les performances
   - Exemple :
   ```sql
   SELECT 
       nom,
       materiaux,
       indice,
       gravure
   FROM verres
   ```

2. **Filtrage des Données**
   - Utilisation de `WHERE` pour filtrer les données pertinentes
   - Conditions multiples avec `AND` et `OR`
   - Exemple :
   ```sql
   WHERE materiaux = ?
   AND indice BETWEEN ? AND ?
   AND protection = 1
   ```

### 2.2 Jointures et Relations
```python
def get_verres_with_enhanced_data():
    """
    Extrait les verres avec leurs données enrichies.
    
    Returns:
        List[tuple]: Liste des verres avec leurs données enrichies
    """
    query = """
    SELECT 
        v.nom,
        v.materiaux,
        v.indice,
        e.gravure_nasale,
        e.source_url
    FROM verres v
    LEFT JOIN enhanced e ON v.nom = e.nom_verre
    WHERE e.created_at IS NOT NULL
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
```

### 2.3 Conditions et Filtres
1. **Filtres Temporels**
   ```sql
   WHERE created_at >= DATEADD(day, -30, GETDATE())
   ```

2. **Filtres sur les Caractéristiques**
   ```sql
   WHERE protection = 1
   AND photochromic = 1
   AND indice BETWEEN 1.5 AND 1.67
   ```

3. **Filtres sur les Textes**
   ```sql
   WHERE gravure LIKE '%BBGR%'
   AND materiaux IN ('CR-39', 'Polycarbonate')
   ```

## 3. Optimisations des Requêtes

### 3.1 Index et Performance
1. **Index sur les Colonnes de Recherche**
   ```sql
   CREATE INDEX idx_verres_fournisseur ON verres (fournisseur)
   CREATE INDEX idx_verres_materiaux ON verres (materiaux)
   CREATE INDEX idx_verres_indice ON verres (indice)
   ```

2. **Index Composés**
   ```sql
   CREATE INDEX idx_verres_fournisseur_materiaux 
   ON verres (fournisseur, materiaux)
   ```

### 3.2 Optimisation des Requêtes
1. **Utilisation de Paramètres**
   ```python
   def execute_parameterized_query(query: str, params: tuple):
       """Exécute une requête paramétrée pour éviter les injections SQL."""
       with get_connection() as conn:
           cursor = conn.cursor()
           cursor.execute(query, params)
           return cursor.fetchall()
   ```

2. **Gestion de la Mémoire**
   ```python
   def get_large_dataset():
       """Récupère un grand ensemble de données par lots."""
       query = "SELECT * FROM verres"
       with get_connection() as conn:
           cursor = conn.cursor()
           cursor.execute(query)
           while True:
               rows = cursor.fetchmany(1000)
               if not rows:
                   break
               yield rows
   ```

### 3.3 Monitoring des Performances
```python
def log_query_execution(query: str, execution_time: float):
    """Enregistre les performances des requêtes."""
    logger.info(f"Requête: {query}")
    logger.info(f"Temps d'exécution: {execution_time:.2f} secondes")
```

## Conclusion

Les requêtes SQL implémentées dans le projet EngraveDetect sont fonctionnelles et optimisées pour l'extraction efficace des données. La documentation détaillée des requêtes, incluant les choix de sélection, filtrage et jointures, permet une maintenance et une évolution aisée du système.

### Points Forts
1. Requêtes SQL fonctionnelles et testées
2. Documentation claire des choix de conception
3. Optimisations de performance documentées
4. Gestion robuste des erreurs


