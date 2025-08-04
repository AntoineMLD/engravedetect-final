# C1. Automatisation de l'Extraction de Données

## Contexte
Ce document décrit l'automatisation réelle de l'extraction de données dans le projet EngraveDetect. Toutes les informations sont vérifiées dans le code et les scripts du projet.

---

## 1. Architecture et objectifs

- **Objectif principal** : Automatiser la collecte, le nettoyage et l'intégration des données de verres optiques dans une base PostgreSQL.
- **Technologies** : Python, Scrapy, SQLAlchemy, FastAPI, Docker, GitHub Actions.
- **Stockage** : Base PostgreSQL (Azure SQL en production), accès via SQLAlchemy.
- **API** : FastAPI pour l'accès aux données et la gestion des utilisateurs.

---

## 2. Extraction automatisée (Scraping)

### a) Spiders Scrapy
- **Fichier principal** : `src/data/scraping/france_optique/spiders/glass_spider.py`
- **Classe** : `GlassSpider(scrapy.Spider)`
- **Rôle** : Extraction des données de verres optiques depuis france-optique.com, parsing HTML, création d'items structurés.
- **Exemple réel** :
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

### b) Pipeline Scrapy
- **Fichier** : `src/data/scraping/france_optique/pipelines.py`
- **Classe** : `PostgresPipeline`
- **Rôle** : Nettoyage HTML, téléchargement d'images, insertion en base `staging` (PostgreSQL).
- **Dépendances** : `sqlalchemy`, `requests`, `BeautifulSoup`, `logging`, `os`, `re`, `time`, `pathlib`

---

## 3. Intégration et nettoyage des données

### a) Nettoyage et préparation
- **Fichier** : `src/data/processing/cleaner.py`
- **Classe** : `OpticalDataCleaner`
- **Rôle** : Chargement depuis `staging`, nettoyage, création de la table `enhanced`, export CSV, insertion en base, statistiques.
- **Dépendances** : `pandas`, `sqlalchemy`, `dotenv`, `logging`, `os`, `csv`, `datetime`

### b) Enrichissement
- **Fichier** : `src/data/processing/enricher.py`
- **Classe** : `DataEnricher`
- **Rôle** : Ajout de tags, variantes, détection de propriétés, gestion des fournisseurs, passage de `enhanced` à `verres`.
- **Dépendances** : `pandas`, `sqlalchemy`, `re`, `json`, `logging`

### c) Corrections post-nettoyage
- **Fichier** : `src/data/processing/fix_enhanced_table.py`
- **Rôle** : Correction des valeurs par défaut, liaison des IDs manquants (fournisseur, matériau) dans `enhanced`.
- **Dépendances** : `sqlalchemy`, `logging`

### d) Import final
- **Fichier** : `src/data/processing/import_enhanced.py`
- **Rôle** : Import du dernier CSV enhanced en base via `OpticalDataCleaner`.
- **Dépendances** : `logging`, `os`, `pathlib`

---

## 4. Orchestration du pipeline

- **Fichier** : `src/orchestrator/pipeline_manager.py`
- **Classe** : `PipelineManager`
- **Rôle** : Orchestration complète du pipeline (scraping, nettoyage, enrichissement, corrections, import, etc.).
- **Dépendances** : `logging`, `pathlib`, `scrapy`, `src.data.processing.cleaner`, etc.

---

## 5. Commandes d’exécution principales

```bash
# 1. Lancer le scraping (exemple)
scrapy crawl glass_spider

# 2. Nettoyer et créer la table enhanced
python -m src.data.processing.cleaner

# 3. Enrichir les données
python -m src.data.processing.enricher

# 4. Corriger la table enhanced
python src/data/processing/fix_enhanced_table.py

# 5. Importer le CSV enhanced en base
python src/data/processing/import_enhanced.py

# 6. Orchestration complète (optionnel)
python -m src.orchestrator.pipeline_manager
```

---

## 6. Gestion des logs et des erreurs

- Tous les scripts utilisent le module `logging` pour tracer les étapes, erreurs, et statistiques.
- Les erreurs critiques sont loguées et lèvent des exceptions explicites.
- Les scripts de correction et d’import vérifient l’intégrité des données après chaque étape.

---

## Conclusion

L’automatisation de l’extraction de données dans EngraveDetect repose sur des spiders Scrapy robustes, un pipeline de nettoyage et d’enrichissement modulaire, et une orchestration centralisée. Toutes les étapes, scripts et dépendances sont explicitement listés et vérifiés dans le code du projet.

