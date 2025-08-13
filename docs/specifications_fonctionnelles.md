# Spécifications Fonctionnelles — EngraveDetect

## 1. Contexte du projet

EngraveDetect est une application web dédiée aux professionnels de l'optique, leur permettant d'identifier les verres optiques à partir d'une gravure nasale dessinée. L'outil vise à simplifier et fiabiliser un processus aujourd'hui manuel, fastidieux, et sujet à erreur.

## 2. Objectifs fonctionnels

- Permettre à l'utilisateur de s'authentifier via un système sécurisé (JWT).
- Accéder à une interface intuitive avec canevas de dessin, zone de saisie de tags, et bouton de validation.
- Envoyer une requête à une API IA pour retrouver les verres les plus similaires.
- Afficher dynamiquement une liste de résultats cliquables.
- Accéder aux détails d'un verre via une modale d'information.

## 3. Parcours utilisateur

![Parcours utilisateur](./docs/assets/parcours_utilisateur.png)

## 4. Modèle de données (E/R)

![Modèle de données](./docs/assets/schema_er.png)

## 5. User Stories avec Critères d'Acceptation

### **ÉPIC 1 : Authentification et Gestion des Utilisateurs**

#### **US-001 : Connexion utilisateur**
**En tant que** opticien professionnel  
**Je veux** me connecter à l'application avec mes identifiants  
**Afin de** accéder aux fonctionnalités de recherche de verres

**Critères d'acceptation :**
- [ ] L'utilisateur peut saisir son nom d'utilisateur et mot de passe
- [ ] Le système valide les identifiants et génère un token JWT
- [ ] Le token est stocké en localStorage pour les sessions suivantes
- [ ] L'utilisateur est redirigé vers l'interface principale après connexion
- [ ] Les messages d'erreur sont affichés en cas d'identifiants incorrects
- [ ] Le token expire automatiquement après 30 minutes

#### **US-002 : Inscription d'un nouvel utilisateur**
**En tant que** opticien professionnel  
**Je veux** créer un compte utilisateur  
**Afin de** accéder à l'application pour la première fois

**Critères d'acceptation :**
- [ ] L'utilisateur peut saisir son email, nom d'utilisateur et mot de passe
- [ ] Le système valide le format de l'email
- [ ] Le mot de passe est hashé avec bcrypt avant stockage
- [ ] L'utilisateur doit accepter la politique de confidentialité (RGPD)
- [ ] Un message de succès confirme la création du compte
- [ ] L'utilisateur est automatiquement connecté après inscription

#### **US-003 : Accès aux données personnelles (RGPD)**
**En tant que** utilisateur connecté  
**Je veux** accéder à mes données personnelles  
**Afin de** vérifier les informations stockées sur mon compte

**Critères d'acceptation :**
- [ ] L'utilisateur peut consulter son username et email via l'API `/me`
- [ ] Les données sont retournées au format JSON
- [ ] Seul l'utilisateur authentifié peut accéder à ses propres données
- [ ] L'accès est sécurisé par token JWT

#### **US-004 : Suppression de compte (Droit à l'oubli RGPD)**
**En tant que** utilisateur connecté  
**Je veux** supprimer mon compte  
**Afin de** exercer mon droit à l'oubli

**Critères d'acceptation :**
- [ ] L'utilisateur peut supprimer son compte via l'API `/me` (DELETE)
- [ ] Toutes les données personnelles sont supprimées de la base
- [ ] Le token JWT devient invalide immédiatement
- [ ] Un message confirme la suppression du compte
- [ ] L'utilisateur est redirigé vers la page de connexion

#### **US-005 : Déconnexion**
**En tant que** utilisateur connecté  
**Je veux** me déconnecter de l'application  
**Afin de** sécuriser ma session

**Critères d'acceptation :**
- [ ] L'utilisateur peut cliquer sur le bouton "Déconnexion"
- [ ] Le token JWT est supprimé du localStorage
- [ ] L'utilisateur est redirigé vers la page de connexion
- [ ] L'accès aux fonctionnalités est bloqué après déconnexion

---

### **ÉPIC 2 : Interface de Dessin et Recherche IA**

#### **US-006 : Dessin d'une gravure**
**En tant que** opticien  
**Je veux** dessiner une gravure sur un canvas  
**Afin de** représenter visuellement la gravure à identifier

**Critères d'acceptation :**
- [ ] Le canvas est accessible via souris et tactile
- [ ] Le dessin s'affiche en temps réel pendant la saisie
- [ ] L'épaisseur du trait est adaptée pour la précision
- [ ] Le canvas est responsive (400x400px sur desktop)
- [ ] Les instructions d'utilisation sont accessibles (ARIA)
- [ ] La touche Espace efface le dessin

#### **US-007 : Effacement du dessin**
**En tant que** opticien  
**Je veux** effacer le dessin en cours  
**Afin de** recommencer un nouveau dessin

**Critères d'acceptation :**
- [ ] Le bouton " Effacer le dessin" est visible et accessible
- [ ] Le canvas est vidé complètement lors du clic
- [ ] L'action est confirmée visuellement
- [ ] Le bouton est désactivé si le canvas est déjà vide

#### **US-008 : Recherche de symboles similaires par IA**
**En tant que** opticien  
**Je veux** rechercher des symboles similaires à mon dessin  
**Afin de** identifier les gravures correspondantes

**Critères d'acceptation :**
- [ ] Le bouton " Rechercher les symboles similaires" lance la recherche
- [ ] L'image du canvas est envoyée à l'API `/match`
- [ ] Les 20 meilleures correspondances sont affichées
- [ ] Chaque résultat montre l'image, le nom et le score de similarité
- [ ] Les résultats sont triés par score décroissant
- [ ] Un indicateur de chargement est affiché pendant la recherche
- [ ] Les erreurs de recherche sont gérées et affichées

---

### **ÉPIC 3 : Gestion des Tags et Recherche de Verres**

#### **US-009 : Sélection de tags depuis les résultats IA**
**En tant que** opticien  
**Je veux** sélectionner des tags depuis les résultats de recherche  
**Afin de** constituer une liste de critères de recherche

**Critères d'acceptation :**
- [ ] Chaque résultat IA a un bouton " Ajouter ce tag"
- [ ] Le tag sélectionné apparaît dans la section "Tags sélectionnés"
- [ ] Les tags dupliqués ne sont pas ajoutés
- [ ] Chaque tag a un bouton "×" pour le supprimer
- [ ] La liste des tags est mise à jour dynamiquement

#### **US-010 : Ajout manuel de tags**
**En tant que** opticien  
**Je veux** ajouter manuellement des tags texte  
**Afin de** compléter la recherche avec des informations spécifiques

**Critères d'acceptation :**
- [ ] Un champ de saisie permet d'ajouter des tags manuellement
- [ ] Le bouton " Ajouter ces tags" traite la saisie
- [ ] Les tags sont séparés par des espaces ou virgules
- [ ] Les tags vides ou dupliqués sont ignorés
- [ ] Les tags ajoutés apparaissent dans la liste des tags sélectionnés

#### **US-011 : Réinitialisation des tags**
**En tant que** opticien  
**Je veux** réinitialiser tous les tags sélectionnés  
**Afin de** recommencer une nouvelle recherche

**Critères d'acceptation :**
- [ ] Le bouton " Réinitialiser les tags" vide la liste
- [ ] Tous les tags (IA et manuels) sont supprimés
- [ ] L'action est confirmée visuellement
- [ ] Le bouton est désactivé si aucun tag n'est sélectionné

#### **US-012 : Recherche de verres avec tags**
**En tant que** opticien  
**Je veux** rechercher des verres correspondant aux tags sélectionnés  
**Afin de** identifier les verres optiques appropriés

**Critères d'acceptation :**
- [ ] Le bouton " Rechercher les verres correspondants" lance la recherche
- [ ] Les tags sont envoyés à l'API `/search_tags`
- [ ] Les verres correspondants sont affichés dans une liste
- [ ] Chaque verre affiche : nom, fournisseur, indice, image de gravure
- [ ] Les résultats sont paginés (100 par page par défaut)
- [ ] Un message indique le nombre de verres trouvés
- [ ] Les erreurs de recherche sont gérées et affichées

---

### **ÉPIC 4 : Consultation des Détails des Verres**

#### **US-013 : Affichage des détails d'un verre**
**En tant que** opticien  
**Je veux** consulter les détails complets d'un verre  
**Afin de** obtenir toutes les informations techniques nécessaires

**Critères d'acceptation :**
- [ ] Le clic sur "Voir les détails" ouvre une modale
- [ ] La modale affiche toutes les informations du verre :
  - ID, nom, variante, fournisseur
  - Indice, hauteur min/max
  - Matériau (nom et description)
  - Série (nom et description)
  - Traitements appliqués
  - Tags associés
  - Image complète de la gravure
- [ ] La modale est accessible au clavier (focus trap)
- [ ] Le bouton "×" ferme la modale
- [ ] L'overlay permet de fermer la modale en cliquant à l'extérieur

#### **US-014 : Actualisation des données d'un verre**
**En tant que** opticien  
**Je veux** actualiser les données d'un verre  
**Afin de** obtenir les informations les plus récentes

**Critères d'acceptation :**
- [ ] Le bouton " Actualiser les données" recharge les informations
- [ ] Les données sont récupérées depuis l'API `/verre/{id}`
- [ ] Un indicateur de chargement est affiché pendant l'actualisation
- [ ] Les données mises à jour remplacent les anciennes
- [ ] Les erreurs d'actualisation sont gérées et affichées

---

### **ÉPIC 5 : Monitoring et Dashboard**

#### **US-015 : Accès au dashboard de monitoring**
**En tant que** opticien  
**Je veux** accéder au dashboard de monitoring  
**Afin de** surveiller les performances du système

**Critères d'acceptation :**
- [ ] Le bouton " Dashboard" est visible dans l'interface
- [ ] Le clic ouvre Grafana dans un nouvel onglet
- [ ] L'URL du dashboard est : `http://37.27.217.233:3001/d/engravedetect/engravedetect-monitoring-modele-ia`
- [ ] Le dashboard affiche les métriques en temps réel
- [ ] Le rafraîchissement automatique est configuré (30s)

---

### **ÉPIC 6 : Accessibilité et Expérience Utilisateur**

#### **US-016 : Conformité WCAG 2.1**
**En tant que** utilisateur avec handicap  
**Je veux** utiliser l'application avec des outils d'assistance  
**Afin de** accéder à toutes les fonctionnalités

**Critères d'acceptation :**
- [ ] Les contrastes respectent le ratio 4.5:1 minimum
- [ ] La navigation au clavier est possible sur tous les éléments
- [ ] Les images ont des attributs alt descriptifs
- [ ] La structure HTML utilise les balises H1-H6 correctement
- [ ] Les formulaires ont des labels associés
- [ ] Les messages d'erreur/succès sont accessibles (aria-live)
- [ ] Les modales sont conformes (aria-modal, focus trap)

#### **US-017 : Design responsive**
**En tant que** opticien  
**Je veux** utiliser l'application sur différents écrans  
**Afin de** travailler depuis n'importe quel appareil

**Critères d'acceptation :**
- [ ] L'interface s'adapte aux écrans desktop (1200px+)
- [ ] L'interface s'adapte aux tablettes (768px-1199px)
- [ ] L'interface s'adapte aux mobiles (480px-767px)
- [ ] Le canvas reste utilisable sur tous les formats
- [ ] Les boutons et textes restent lisibles
- [ ] La navigation reste intuitive sur mobile

---

### **ÉPIC 7 : Sécurité et Performance**

#### **US-018 : Sécurité des API**
**En tant que** administrateur système  
**Je veux** que les API soient sécurisées  
**Afin de** protéger les données des utilisateurs

**Critères d'acceptation :**
- [ ] Toutes les routes sensibles nécessitent un token JWT valide
- [ ] Les tokens expirent automatiquement (30 minutes)
- [ ] Les mots de passe sont hashés avec bcrypt
- [ ] Les headers de sécurité sont configurés (CSP, X-Frame-Options)
- [ ] La validation des entrées est stricte (Pydantic)
- [ ] Les logs de sécurité sont générés

#### **US-019 : Rate limiting**
**En tant que** administrateur système  
**Je veux** limiter le nombre de requêtes par utilisateur  
**Afin de** prévenir les abus et protéger les ressources

**Critères d'acceptation :**
- [ ] `/embedding` : 5 requêtes/minute maximum
- [ ] `/match` : 5 requêtes/minute maximum
- [ ] `/search_tags` : 10 requêtes/minute maximum
- [ ] `/verre/{id}` : 20 requêtes/minute maximum
- [ ] Les dépassements retournent une erreur 429
- [ ] Les limites sont configurables

#### **US-020 : Monitoring des performances**
**En tant que** administrateur système  
**Je veux** surveiller les performances du modèle IA  
**Afin de** garantir la qualité du service

**Critères d'acceptation :**
- [ ] Les métriques sont exposées via `/metrics` (Prometheus)
- [ ] Le statut de santé est accessible via `/model/health`
- [ ] Les métriques incluent : accuracy, latence, throughput
- [ ] La détection de drift est implémentée
- [ ] Les alertes sont configurées pour les seuils critiques
- [ ] Le dashboard Grafana affiche les métriques en temps réel

---

### **ÉPIC 8 : Récolte et Préparation des Données**

#### **US-021 : Collecte automatique des données de verres**
**En tant que** administrateur système  
**Je veux** collecter automatiquement les données de verres depuis les fournisseurs  
**Afin de** maintenir une base de données à jour

**Critères d'acceptation :**
- [ ] Le script de collecte s'exécute automatiquement via cron
- [ ] Les données sont extraites depuis les sources configurées
- [ ] Les nouvelles données sont insérées dans la table `staging`
- [ ] Les données existantes sont mises à jour si nécessaire
- [ ] Les logs de collecte sont générés avec timestamp
- [ ] Les erreurs de collecte sont gérées et notifiées
- [ ] La conformité RGPD est respectée (source_url, created_at)

#### **US-022 : Nettoyage et validation des données**
**En tant que** administrateur système  
**Je veux** nettoyer et valider les données collectées  
**Afin de** garantir la qualité des données d'entraînement

**Critères d'acceptation :**
- [ ] Les données dupliquées sont identifiées et supprimées
- [ ] Les valeurs manquantes sont détectées et signalées
- [ ] Les formats de données sont validés (indice, hauteur, etc.)
- [ ] Les données invalides sont rejetées avec justification
- [ ] Les données nettoyées sont transférées vers la table `enhanced`
- [ ] Un rapport de qualité des données est généré
- [ ] Les métriques de qualité sont exposées via API

#### **US-023 : Enrichissement des données avec tags**
**En tant que** administrateur système  
**Je veux** enrichir les données avec des tags descriptifs  
**Afin de** améliorer la recherche et la classification

**Critères d'acceptation :**
- [ ] Les tags sont extraits automatiquement des descriptions
- [ ] Les tags sont normalisés (minuscules, accents, etc.)
- [ ] Les tags dupliqués sont consolidés
- [ ] Les tags sont associés aux verres dans la table `verres`
- [ ] Un dictionnaire de tags est maintenu et accessible
- [ ] Les nouveaux tags sont détectés et ajoutés automatiquement
- [ ] La cohérence des tags est vérifiée régulièrement

#### **US-024 : Gestion des images de gravures**
**En tant que** administrateur système  
**Je veux** gérer les images de gravures de manière optimisée  
**Afin de** réduire l'espace de stockage et améliorer les performances

**Critères d'acceptation :**
- [ ] Les images sont redimensionnées à 400x400px
- [ ] Les images sont compressées (format JPG, qualité 85%)
- [ ] Les métadonnées EXIF sont supprimées pour la confidentialité
- [ ] Les images sont stockées dans `/data/augmented_gravures/`
- [ ] Les images sont organisées par catégorie de gravure
- [ ] Les images corrompues sont détectées et remplacées
- [ ] Un index des images est maintenu pour la recherche rapide

---

### **ÉPIC 9 : Développement et Entraînement du Modèle IA**

#### **US-025 : Préparation du dataset d'entraînement**
**En tant que** data scientist  
**Je veux** préparer un dataset équilibré pour l'entraînement  
**Afin de** optimiser les performances du modèle

**Critères d'acceptation :**
- [ ] Le dataset est divisé en train/validation/test (70/15/15)
- [ ] Les classes sont équilibrées (oversampling si nécessaire)
- [ ] Les images sont augmentées (rotation, zoom, bruit)
- [ ] Les labels sont encodés en one-hot encoding
- [ ] Le dataset est sauvegardé dans `/data/datasets/`
- [ ] Les métriques de répartition sont documentées
- [ ] Le dataset est versionné avec Git LFS

#### **US-026 : Entraînement du modèle EfficientNet**
**En tant que** data scientist  
**Je veux** entraîner un modèle EfficientNet pour la classification  
**Afin de** obtenir une reconnaissance précise des gravures

**Critères d'acceptation :**
- [ ] Le modèle EfficientNet-B0 est utilisé comme architecture de base
- [ ] L'entraînement utilise PyTorch avec GPU si disponible
- [ ] Les hyperparamètres sont optimisés (learning rate, batch size)
- [ ] L'early stopping est configuré pour éviter l'overfitting
- [ ] Les métriques d'entraînement sont sauvegardées (loss, accuracy)
- [ ] Le modèle est sauvegardé dans `/src/models/`
- [ ] Un rapport d'entraînement est généré avec les performances

#### **US-027 : Évaluation et validation du modèle**
**En tant que** data scientist  
**Je veux** évaluer les performances du modèle entraîné  
**Afin de** valider sa qualité avant déploiement

**Critères d'acceptation :**
- [ ] Les métriques de performance sont calculées (accuracy, precision, recall, F1)
- [ ] La matrice de confusion est générée et analysée
- [ ] Les prédictions erronées sont analysées pour amélioration
- [ ] Le modèle est testé sur des données non vues
- [ ] Les performances sont comparées aux benchmarks
- [ ] Un rapport d'évaluation détaillé est généré
- [ ] Les seuils de confiance sont optimisés

#### **US-028 : Déploiement du modèle en production**
**En tant que** administrateur système  
**Je veux** déployer le modèle entraîné en production  
**Afin de** rendre le service IA disponible aux utilisateurs

**Critères d'acceptation :**
- [ ] Le modèle est chargé dans l'API IA au démarrage
- [ ] Les endpoints `/embedding` et `/match` sont fonctionnels
- [ ] Les performances en production sont surveillées
- [ ] Le modèle est versionné et peut être rollbacké
- [ ] Les logs de prédiction sont générés pour audit
- [ ] Le modèle est sauvegardé avec ses métadonnées
- [ ] Un processus de déploiement automatisé est en place

#### **US-029 : Mise à jour et amélioration continue du modèle**
**En tant que** data scientist  
**Je veux** améliorer continuellement le modèle avec de nouvelles données  
**Afin de** maintenir et améliorer les performances

**Critères d'acceptation :**
- [ ] Un processus de retraining automatique est configuré
- [ ] Les nouvelles données sont intégrées progressivement
- [ ] La détection de concept drift est implémentée
- [ ] Les performances sont comparées avant/après mise à jour
- [ ] Le modèle n'est mis à jour que si les performances s'améliorent
- [ ] Un historique des versions du modèle est maintenu
- [ ] Les utilisateurs sont notifiés des améliorations

#### **US-030 : Gestion des embeddings et recherche par similarité**
**En tant que** data scientist  
**Je veux** générer et gérer les embeddings des images  
**Afin de** permettre la recherche par similarité

**Critères d'acceptation :**
- [ ] Les embeddings sont générés pour toutes les images d'entraînement
- [ ] Les embeddings sont normalisés (cosine similarity)
- [ ] Un index de similarité est créé pour la recherche rapide
- [ ] L'endpoint `/embedding` génère les embeddings à la volée
- [ ] L'endpoint `/match` utilise la similarité cosinus
- [ ] Les résultats sont triés par score de similarité décroissant
- [ ] Les performances de recherche sont optimisées (< 2 secondes)

---

## 6. Contraintes techniques

- API principale : FastAPI (`/api`) — CRUD sécurisé avec SQL Server
- API IA : FastAPI (`/api_ia`) — endpoints : `/embedding`, `/match`, `/search_tags`
- Authentification : JWT, OAuth2PasswordBearer
- Front-end : HTML/CSS/JS vanilla (pas de framework)
- Monitoring : Prometheus + Grafana (Docker)
- Sécurité : middleware de headers HTTP, MIME check, JWT expiration
- Base de données : Azure SQL (modèle complet via SQLAlchemy)

## 7. Accessibilité et expérience utilisateur

- ‍ Interface contrastée, responsive, lisible sur tablette
-  Application légère, chargement asynchrone
-  Focus mis sur la rapidité d'exécution du modèle IA et la clarté des résultats

###  Accessibilité (conformité RGAA/WCAG)

L'interface utilisateur de l'application EngraveDetect a été conçue en respectant les principes d'accessibilité définis dans les référentiels RGAA 4.1 et WCAG 2.1. Voici l'état actuel de l'implémentation :

| Critère RGAA/WCAG | Implémenté ? | Emplacement / Détails |
|-------------------|--------------|----------------------|
| Contraste minimum (4.5:1) |  | - Texte principal : `#202124` sur blanc (16:1)<br>- Boutons : `#1a5fb4` sur blanc (7:1)<br>- Focus : `#667eea` avec outline blanc |
| Navigation clavier |  | - Focus piégé dans la modale<br>- Touche Espace pour effacer le canvas<br>- Focus visible sur tous les éléments<br>- Manque : raccourcis clavier supplémentaires |
| Structure Hn correcte |  | - `h1` : Titre principal "Connexion à EngraveDetect"<br>- `h2` : Sections (Dessin, Tags, etc.)<br>- `h3` : Sous-sections (Résultats) |
| Attributs alt sur les images |  | - Logo : "EngraveDetect Logo"<br>- Canvas : aria-label "Zone de dessin pour la gravure"<br>- Gravures : descriptions spécifiques |
| Feedback utilisateur accessible |  | - Messages d'erreur/succès avec `aria-live`<br>- Formulaires avec `aria-describedby`<br>- Modales avec `aria-modal`<br>- À améliorer : retours sonores et haptiques |

Note :  = Complètement implémenté,  = Partiellement implémenté

Les améliorations prévues incluent :
- Ajout de raccourcis clavier pour les actions principales
- Amélioration des retours sonores et haptiques
- Extension des descriptions ARIA pour les actions complexes
