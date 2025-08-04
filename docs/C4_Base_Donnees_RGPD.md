# C4. Base de Données et Conformité RGPD

## Contexte
Ce document présente la modélisation et l'implémentation de la base de données du projet EngraveDetect. Le projet utilise PostgreSQL comme système de gestion de base de données relationnelle, avec SQLAlchemy comme ORM.

---

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

#### Entité Utilisateur : USERS
- Identifiant : id (PK)
- Propriétés :
  - username (String) : Nom d'utilisateur unique
  - email (String) : Email unique
  - hashed_password (String) : Mot de passe hashé
  - is_active (Boolean) : Statut du compte

### 1.2 Modèle Logique de Données (MLD)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE verres (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(500) NOT NULL,
    materiaux VARCHAR(100),
    indice FLOAT,
    fournisseur VARCHAR(200),
    gravure VARCHAR(1000),
    url_source VARCHAR(500),
    variante VARCHAR(200),
    hauteur_min INTEGER,
    hauteur_max INTEGER,
    protection BOOLEAN DEFAULT FALSE,
    photochromic BOOLEAN DEFAULT FALSE,
    tags VARCHAR(500),
    image_gravure VARCHAR(500)
);
```

### 1.3 Modèle Physique de Données (MPD)

#### Index
```sql
CREATE INDEX idx_verres_fournisseur ON verres(fournisseur);
CREATE INDEX idx_verres_materiaux ON verres(materiaux);
CREATE INDEX idx_verres_indice ON verres(indice);
CREATE INDEX idx_users_email ON users(email);
```

#### Contraintes
```sql
ALTER TABLE verres
ADD CONSTRAINT chk_indice CHECK (indice >= 1.0 AND indice <= 2.0);
ALTER TABLE verres
ADD CONSTRAINT chk_hauteur CHECK (hauteur_min <= hauteur_max);
```

---

## 2. Implémentation de la Base de Données

### 2.1 Configuration de la Connexion
```python
# src/api/core/config.py
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
```

### 2.2 Modèle SQLAlchemy
```python
# src/api/models/verres.py
class Verre(Base):
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

# src/api/core/auth/models.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
```

---

## 3. Conformité RGPD

### 3.1 Nature des Données

Le projet EngraveDetect traite :
- Données techniques (verres, images, fournisseurs)
- **Données personnelles** : email, username, mot de passe (hashé) pour la gestion des comptes utilisateurs

### 3.2 Registre des Traitements

#### 1. Gestion des comptes utilisateurs
- **Finalité** : Création, gestion et suppression de comptes utilisateurs
- **Base légale** : Consentement explicite de l'utilisateur
- **Données concernées** : email, username, mot de passe (hashé)
- **Durée de conservation** : Jusqu'à suppression du compte par l'utilisateur
- **Droits** : Accès, rectification, suppression, portabilité

#### 2. Collecte et traitement des données verres
- **Finalité** : Identification, analyse et classification des verres optiques
- **Base légale** : Intérêt légitime
- **Données concernées** : Caractéristiques techniques, images, fournisseurs
- **Durée de conservation** : 5 ans

### 3.3 Procédures de Conformité RGPD

#### Consentement et politique de confidentialité
- Consentement explicite requis à l'inscription (case à cocher, lien vers la politique de confidentialité)
- Politique de confidentialité accessible sur le site (`src/front/confidentialite.html`)

#### Accès et suppression des données personnelles
- **Accès** : route API `/me` (GET) pour récupérer ses données personnelles (username, email)
- **Suppression** : route API `/me` (DELETE) pour supprimer son compte (droit à l'oubli)
- Suppression effective des données utilisateur en base

#### Sécurité des données personnelles
- Mots de passe stockés hashés (jamais en clair)
- Emails stockés en clair (pas de hash, car non obligatoire RGPD)
- Accès à la base restreint, logs de sécurité, sauvegardes

#### Procédure de notification
- En cas de violation de données, notification à la CNIL et aux utilisateurs concernés (procédure à documenter)

### 3.4 Documentation et registre technique
- Registre des traitements à jour (voir ci-dessus)
- Documentation technique sur la gestion des utilisateurs et des droits RGPD
- Tests automatisés pour les routes RGPD

---

## 4. Documentation Technique

### 4.1 Dépendances
```python
# requirements.txt (extrait)
fastapi
sqlalchemy
pydantic
python-dotenv
passlib
PyJWT
slowapi
prometheus_client
python-magic
pillow
```

### 4.2 Commandes d'Exécution
```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration de la base de données
python src/database/reset_database.py
```

---

## Conclusion

La base de données du projet EngraveDetect gère à la fois des données techniques et des données personnelles. Elle respecte les exigences du RGPD grâce à une structure de données claire, des procédures d'accès/suppression, et une politique de confidentialité accessible. Les droits des utilisateurs sont garantis par des routes API dédiées et des tests automatisés.

### Points Forts
1. Modélisation Merise claire et cohérente
2. Gestion complète des comptes utilisateurs (RGPD)
3. Procédures d'accès/suppression conformes RGPD
4. Documentation technique et registre des traitements à jour
5. Sécurité des accès et des données 