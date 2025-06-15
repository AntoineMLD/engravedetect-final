# C1. Automatisation de l'Extraction de Données

## Contexte
Ce document analyse l'implémentation de l'automatisation de l'extraction de données dans le projet EngraveDetect, un système de gestion de données optiques. Le projet vise à automatiser la collecte et le stockage des données des verres optiques.

## Analyse des Critères d'Évaluation

### 1. Présentation du Projet et Contexte

#### Acteurs
- **Utilisateurs finaux** : Opticiens et professionnels de l'optique
- **Équipe de développement** : Développeurs Python, DevOps
- **Partenaires** : Fournisseurs de services cloud (Azure)

#### Objectifs Fonctionnels
Le projet vise à :
- Automatiser la collecte des données des verres optiques
- Centraliser les données dans une base Azure SQL
- Fournir une API REST pour l'accès aux données
- Assurer un stockage structuré et sécurisé des données

#### Objectifs Techniques
- Mise en place d'un système de scraping automatisé
- Développement d'une API REST sécurisée
- Stockage structuré dans Azure SQL
- Gestion des erreurs et monitoring

### 2. Spécifications Techniques

#### Technologies et Outils
- **Backend** : Python avec FastAPI
- **Base de données** : Azure SQL
- **Scraping** : Scrapy
- **DevOps** : Docker, GitHub Actions

#### Services Externes
- **Azure SQL** : Base de données principale
- **GitHub** : Gestion du code source et CI/CD
- **Docker Hub** : Distribution des images Docker

### 3. Périmètre des Spécifications Techniques

#### Extraction depuis les Pages Web (Scraping)
Le système utilise Scrapy pour le scraping de données optiques :

1. **Spiders Spécialisés**
   ```python
   class GlassSpider(scrapy.Spider):
       name = "glass_spider"
       allowed_domains = ["www.france-optique.com"]
       start_urls = [
           "https://www.france-optique.com/fournisseur/1344-bbgr-optique/gravures",
           "https://www.france-optique.com/fournisseur/2399-adn-optis",
       ]

       def parse(self, response):
           fournisseur_nom = response.xpath("/html/body/div[2]/div/div[3]/div[2]/h2/text()").get()
           lines = response.xpath('//*[@id="gravures"]/div[2]//div')
           
           for line in lines:
               item = FranceOptiqueItem()
               item["source_url"] = response.url
               item["nom_verre"] = line.css("div.row.tr:not(.group) div.td.col.s3.m3 p::text").get("")
               item["gravure_nasale"] = line.xpath('.//div[contains(@class, "td")][2]//p[@class="gravure_txt"]/b/text()').get()
               item["indice"] = line.css("div.row.tr:not(.group) div.td.col.s1.m1 p::text").get()
               item["materiaux"] = line.css("div.td.col.s2.m2 p::text").get()
               item["fournisseur"] = fournisseur_nom.strip()
               yield item
   ```

2. **Pipeline de Traitement**
   ```python
   class AzureSQLPipeline:
       def __init__(self):
           # Configuration de la connexion
           self.conn_str = (
               f"DRIVER={driver};"
               f"SERVER={self.server};"
               f"DATABASE={self.database};"
               f"UID={self.username};"
               f"PWD={self.password};"
           )
           
       def process_item(self, item, spider):
           # Nettoyage des données
           item["materiaux"] = self.clean_html_tags(item["materiaux"])
           # Insertion dans la base
           self._insert_into_staging(item, spider)
           return item
   ```

3. **Gestion des Erreurs et Retry**
   ```python
   def download_image_with_retry(self, image_url: str, spider) -> str:
       retry_count = 0
       while retry_count < self.max_retries:
           try:
               response = requests.get(image_url, stream=True, timeout=30)
               if response.status_code == 200:
                   return str(local_image_path)
           except Exception as e:
               retry_count += 1
               time.sleep(self.retry_delay)
   ```

#### Extraction depuis la Base de Données Azure SQL
L'extraction depuis Azure SQL est gérée de manière robuste :

1. **Connexion et Configuration**
   ```python
   def __init__(self):
       # Initialisation de SQLAlchemy
       self.engine = create_engine(settings.DATABASE_URL)
       Base.metadata.create_all(bind=self.engine)
       self.Session = sessionmaker(bind=self.engine)
   ```

2. **Requêtes Optimisées**
   ```python
   def _insert_into_staging(self, item: dict, spider) -> bool:
       try:
           with pyodbc.connect(self.conn_str) as conn:
               cursor = conn.cursor()
               cursor.execute(
                   """
                   INSERT INTO staging (source_url, nom_verre, gravure_nasale, indice, materiaux, fournisseur)
                   VALUES (?, ?, ?, ?, ?, ?)
                   """,
                   (item["source_url"], item["nom_verre"], item["gravure_nasale"],
                    item["indice"], item["materiaux"], item["fournisseur"]),
               )
               conn.commit()
               return True
       except Exception as e:
           spider.logger.error(f"Erreur lors de l'insertion dans staging: {e}")
           return False
   ```

#### API REST pour l'Accès aux Données
L'API FastAPI permet l'accès aux données :

1. **Endpoints de Données**
   ```python
   @app.get("/verre/{verre_id}")
   async def get_verre(verre_id: int):
       try:
           with Session() as session:
               verre = session.query(Verre).filter(Verre.id == verre_id).first()
               if not verre:
                   raise HTTPException(status_code=404, detail="Verre non trouvé")
               return verre
       except Exception as e:
           raise HTTPException(status_code=500, detail=str(e))
   ```

2. **Gestion des Erreurs**
   ```python
   @app.exception_handler(HTTPException)
   async def http_exception_handler(request, exc):
       return JSONResponse(
           status_code=exc.status_code,
           content={"detail": exc.detail},
       )
   ```

### 4. Fonctionnalité des Scripts d'Extraction

#### Pipeline de Traitement
Le pipeline principal fonctionne selon cette séquence :

1. **Initialisation**
   ```python
   def open_spider(self, spider):
       # Initialisation des ressources
       for url in spider.start_urls:
           self.items_by_url[url] = []
       
       # Nettoyage de la table
       with self.engine.connect() as conn:
           conn.execute(text("TRUNCATE TABLE verres"))
           conn.commit()
   ```

2. **Extraction et Validation**
   ```python
   def _process_gravure_nasale(self, item: dict, spider) -> dict:
       gravure_nasale = item.get("gravure_nasale")
       if gravure_nasale:
           image_url = self.extract_image_url(gravure_nasale)
           if image_url and image_url.startswith(("http", "https")):
               local_image_path = self.download_image_with_retry(image_url, spider)
               item["image_gravure"] = local_image_path
               item["gravure_nasale"] = image_url
   ```

### 5. Structure des Scripts

#### Architecture Logicielle
L'architecture suit un modèle modulaire :

1. **Couche Extraction**
   - Spiders Scrapy pour le web scraping
   - API FastAPI pour l'accès aux données
   - Gestionnaires de connexion SQL

2. **Couche Traitement**
   - Pipelines de nettoyage
   - Validation des données
   - Transformation des formats

3. **Couche Persistance**
   - Gestion des connexions SQL
   - Transactions et rollback
   - Optimisation des requêtes

### 6. Versionnement

#### Gestion du Code
Le versionnement est géré de manière professionnelle :

1. **Structure Git**
   - Branches feature/, develop/, main/
   - Tags de version
   - Pull requests

2. **CI/CD**
   - Tests automatisés
   - Déploiement continu
   - Qualité du code

## Conclusion

Le projet EngraveDetect implémente de manière robuste l'automatisation de l'extraction de données depuis différentes sources. L'architecture est bien pensée, avec une séparation claire des responsabilités et une documentation complète. Les scripts d'extraction sont fonctionnels et maintenables, avec une bonne gestion des erreurs et une intégration efficace avec les services externes.

### Points Forts
1. Architecture modulaire et extensible
2. Documentation technique complète
3. Pipeline d'extraction automatisé robuste
4. Intégration efficace avec Azure SQL
5. Gestion des erreurs et logging

