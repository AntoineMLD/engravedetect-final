# C4. Base de Données et Conformité RGPD

## Contexte
Ce document présente la modélisation et l'implémentation de la base de données du projet EngraveDetect. Le projet utilise Azure SQL comme système de gestion de base de données relationnelle, avec SQLAlchemy comme ORM.

## 1. Modélisation des Données (Merise)

### 1.1 Modèle Conceptuel de Données (MCD)

#### Entité Principale : VERRE
- Identifiant : id (PK)
- Propriétés :
  - nom (String) : Nom du verre
  - materiaux (String) : Matériau du verre
  - indice (Float) : Indice de réfraction
  - fournisseur (String) : Nom du fournisseur
  - gravure (String) : Code de gravure nasale
  - url_source (String) : URL source des données
  - variante (String) : Variante extraite du nom
  - hauteur_min (Integer) : Hauteur minimale
  - hauteur_max (Integer) : Hauteur maximale
  - protection (Boolean) : Présence de protection
  - photochromic (Boolean) : Verre photochromique
  - tags (String) : Tags extraits du nom
  - image_gravure (String) : Chemin vers l'image

### 1.2 Modèle Logique de Données (MLD)

```sql
CREATE TABLE verres (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nom NVARCHAR(500) NOT NULL,
    materiaux NVARCHAR(100),
    indice FLOAT,
    fournisseur NVARCHAR(200),
    gravure NVARCHAR(1000),
    url_source NVARCHAR(500),
    variante NVARCHAR(200),
    hauteur_min INT,
    hauteur_max INT,
    protection BIT DEFAULT 0,
    photochromic BIT DEFAULT 0,
    tags NVARCHAR(500),
    image_gravure NVARCHAR(500)
);
```

### 1.3 Modèle Physique de Données (MPD)

#### Index
```sql
-- Index sur les colonnes fréquemment utilisées pour la recherche
CREATE INDEX idx_verres_fournisseur ON verres(fournisseur);
CREATE INDEX idx_verres_materiaux ON verres(materiaux);
CREATE INDEX idx_verres_indice ON verres(indice);
```

#### Contraintes
```sql
-- Contraintes de validation
ALTER TABLE verres
ADD CONSTRAINT chk_indice CHECK (indice >= 1.0 AND indice <= 2.0);

ALTER TABLE verres
ADD CONSTRAINT chk_hauteur CHECK (hauteur_min <= hauteur_max);
```

## 2. Implémentation de la Base de Données

### 2.1 Configuration de la Connexion
```python
# src/api/core/config.py
class Settings(BaseSettings):
    # Configuration Azure
    AZURE_SERVER: str | None = None
    AZURE_DATABASE: str | None = None
    AZURE_USERNAME: str | None = None
    AZURE_PASSWORD: str | None = None

    @computed_field
    def database_url(self) -> str:
        """Construit la chaîne de connexion ODBC pour Azure SQL Server."""
        if all([self.AZURE_SERVER, self.AZURE_DATABASE, self.AZURE_USERNAME, self.AZURE_PASSWORD]):
            return (
                f"mssql+pyodbc://{self.AZURE_USERNAME}:{self.AZURE_PASSWORD}@"
                f"{self.AZURE_SERVER}/{self.AZURE_DATABASE}?"
                "driver=ODBC+Driver+18+for+SQL+Server&"
                "TrustServerCertificate=yes&"
                "Connection Timeout=30"
            )
        return "sqlite:///./test.db"  # Base de données de test par défaut
```

### 2.2 Modèle SQLAlchemy
```python
# src/api/models/verres.py
class Verre(Base):
    """Modèle SQLAlchemy pour la table verres."""
    __tablename__ = "verres"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(500), nullable=False)
    materiaux = Column(String(100))
    indice = Column(Float)
    fournisseur = Column(String(200))
    gravure = Column(String(1000), nullable=True)
    url_source = Column(String(500))
    variante = Column(String(200))
    hauteur_min = Column(Integer)
    hauteur_max = Column(Integer)
    protection = Column(Boolean, default=False)
    photochromic = Column(Boolean, default=False)
    tags = Column(String(500))
    image_gravure = Column(String(500))
```

## 3. Conformité RGPD

### 3.1 Nature des Données

Le projet EngraveDetect traite principalement des données techniques et non personnelles :
- Caractéristiques des verres optiques (indice, matériaux, etc.)
- Images des gravures nasales
- Informations sur les fournisseurs

Les seules données sensibles sont :
- Identifiants de connexion (login/mot de passe)
- Ces données sont gérées de manière sécurisée via :
  - Stockage des mots de passe hashés
  - Variables d'environnement pour les identifiants
  - Connexion chiffrée à la base de données

### 3.2 Registre des Traitements

#### Traitements de Données
1. **Collecte des Données**
   - Finalité : Identification des verres optiques
   - Base légale : Intérêt légitime
   - Données concernées : 
     - Caractéristiques techniques des verres
     - Images des gravures
   - Durée de conservation : 5 ans

2. **Traitement des Données**
   - Finalité : Analyse et classification des verres
   - Base légale : Intérêt légitime
   - Données concernées : Données techniques des verres
   - Durée de conservation : 5 ans

### 3.3 Procédures de Conformité

#### 1. Réinitialisation de la Base de Données
```python
# src/database/reset_database.py
def reset_database():
    """
    Réinitialise complètement la base de données en :
    1. Supprimant toutes les tables existantes
    2. Recréant les tables avec la bonne structure
    3. Créant les index nécessaires
    """
    try:
        # Créer la connexion
        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            # 1. Supprimer toutes les tables existantes
            tables_to_drop = ["verres", "enhanced", "staging"]
            for table in tables_to_drop:
                conn.execute(text(f"IF OBJECT_ID('{table}', 'U') IS NOT NULL DROP TABLE {table}"))

            # 2. Recréer les tables avec la bonne structure
            # ... (code de création des tables)

            # 3. Créer les index
            conn.execute(text("CREATE INDEX idx_enhanced_fournisseur ON enhanced (fournisseur)"))
            conn.execute(text("CREATE INDEX idx_enhanced_materiaux ON enhanced (materiaux)"))

    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation de la base de données : {e}")
        raise
```

### 3.4 Sécurité des Données Sensibles

#### Gestion des Identifiants
```python
# src/api/core/config.py
class Settings(BaseSettings):
    # Configuration Azure
    AZURE_SERVER: str | None = None
    AZURE_DATABASE: str | None = None
    AZURE_USERNAME: str | None = None
    AZURE_PASSWORD: str | None = None

    @field_validator('AZURE_SERVER', 'AZURE_DATABASE', 'AZURE_USERNAME', 'AZURE_PASSWORD')
    @classmethod
    def validate_azure_config(cls, v: str | None, info) -> str | None:
        if v is not None and not v:
            raise ValueError(f"{info.field_name} ne peut pas être vide")
        return v
```

Les identifiants sont :
- Stockés dans des variables d'environnement
- Validés au démarrage de l'application
- Utilisés uniquement pour la connexion à la base de données
- Protégés par le chiffrement de la connexion Azure SQL

## 4. Documentation Technique

### 4.1 Dépendances
```python
# requirements.txt
pyodbc==4.0.39
sqlalchemy==2.0.0
pydantic==2.0.0
python-dotenv==1.0.0
```

### 4.2 Commandes d'Exécution
```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration de la base de données
python src/database/migrate_to_verres.py

# Réinitialisation de la base de données (si nécessaire)
python src/database/reset_database.py
```

## Conclusion

La base de données du projet EngraveDetect est conçue selon la méthode Merise et implémentée avec Azure SQL. Elle respecte les exigences du RGPD grâce à une structure de données claire et des procédures de maintenance documentées.

### Points Forts
1. Modélisation Merise claire et cohérente
2. Implémentation robuste avec Azure SQL et SQLAlchemy
3. Documentation technique détaillée
4. Gestion des erreurs et des cas limites
5. Procédures de maintenance documentées 