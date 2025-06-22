# Spécifications Fonctionnelles — EngraveDetect

## 1. Contexte du projet

EngraveDetect est une application web dédiée aux professionnels de l’optique, leur permettant d’identifier les verres optiques à partir d’une gravure nasale dessinée. L’outil vise à simplifier et fiabiliser un processus aujourd’hui manuel, fastidieux, et sujet à erreur.

## 2. Objectifs fonctionnels

- Permettre à l’utilisateur de s’authentifier via un système sécurisé (JWT).
- Accéder à une interface intuitive avec canevas de dessin, zone de saisie de tags, et bouton de validation.
- Envoyer une requête à une API IA pour retrouver les verres les plus similaires.
- Afficher dynamiquement une liste de résultats cliquables.
- Accéder aux détails d’un verre via une modale d’information.

## 3. Parcours utilisateur

![Parcours utilisateur](./docs/assets/parcours_utilisateur.png)

## 4. Modèle de données (E/R)

![Modèle de données](./docs/assets/schema_er.png)

## 5. Fonctionnalités

### 5.1 Authentification
- ✅ Login utilisateur avec `username` + `password` → JWT reçu
- ✅ Token stocké en `localStorage`
- 🔐 Rejet des requêtes si token expiré

### 5.2 Zone de dessin
- 🖊 Canevas HTML5 pour dessiner une gravure
- 🧠 Option de prédiction IA depuis l’image encodée

### 5.3 Tags libres
- 📝 Input libre permettant d’ajouter un ou plusieurs tags
- 🔍 Ces tags sont utilisés par l’API IA pour améliorer la recherche

### 5.4 Bouton "Valider / Match IA"
- ⏳ Lancement d’une requête vers `/match` (FastAPI IA)
- 🎯 Renvoie une liste de verres similaires avec score de similarité

### 5.5 Résultats IA
- 📜 Liste ordonnée de verres
- 🖼️ Chaque carte contient image, nom, fournisseur, tags

### 5.6 Modale de détails
- 💬 Clic sur un verre → ouverture d’une modale avec :
  - Gravure
  - Tags
  - Détails techniques (indice, matériau, hauteur, etc.)

### 5.7 Déconnexion
- 🔓 Bouton → suppression du token + retour à l’écran de connexion

## 6. Contraintes techniques

- API principale : FastAPI (`/api`) — CRUD sécurisé avec SQL Server
- API IA : FastAPI (`/api_ia`) — endpoints : `/embedding`, `/match`, `/search_tags`
- Authentification : JWT, OAuth2PasswordBearer
- Front-end : HTML/CSS/JS vanilla (pas de framework)
- Monitoring : Prometheus + Grafana (Docker)
- Sécurité : middleware de headers HTTP, MIME check, JWT expiration
- Base de données : Azure SQL (modèle complet via SQLAlchemy)

## 7. Accessibilité et expérience utilisateur

- 🧑‍🦯 Interface contrastée, responsive, lisible sur tablette
- 🚀 Application légère, chargement asynchrone
- 🎯 Focus mis sur la rapidité d’exécution du modèle IA et la clarté des résultats

