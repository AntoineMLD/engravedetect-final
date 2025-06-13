import logging

import scrapy

from src.data.scraping.france_optique.items import FranceOptiqueItem


class GlassSpiderFullXPath(scrapy.Spider):
    name = "glass_spider_full_xpath"
    allowed_domains = ["www.france-optique.com"]
    start_urls = [
        "https://www.france-optique.com/gravures/fournisseur=70",
        "https://www.france-optique.com/gravures/fournisseur=521",
    ]

    def parse(self, response):
        self.log(f"Analyse de la page: {response.url}", level=logging.INFO)

        # Récupérer le nom du fournisseur
        fournisseur_nom = response.xpath("/html/body/div[2]/div/div[3]/div/div/div/text()").get()

        # Sélectionner les lignes avec full XPath
        lines = response.xpath('//div[contains(@class, "row") and contains(@class, "tr")]')

        for line in lines:
            item = FranceOptiqueItem()

            # Ajoute l'URL source à l'item
            item["source_url"] = response.url

            # Extraction du nom du verre avec full XPath
            nom_verre = line.xpath('.//div[contains(@class, "td")][4]/p/text()').get()
            if not nom_verre or not nom_verre.strip():
                continue
            item["nom_verre"] = nom_verre.strip()

            # Extraction de la gravure nasale
            gravure_nasale = line.xpath('.//img[contains(@src, "nasal/")]').get()
            if not gravure_nasale:
                continue
            item["gravure_nasale"] = gravure_nasale.strip()

            # Extraction de l'indice et du matériau avec full XPath
            indice = line.xpath('.//div[@class="td col s1 m1"][4]/p/text()').get()
            materiaux = line.xpath("/html/body/div[2]/div/div[4]/div/div/div[1]/div[4]/div[6]/p").get()
            if not indice or not materiaux:
                continue
            item["indice"] = indice.strip()
            item["materiaux"] = materiaux.strip()

            # Ajout du nom du fournisseur de verre
            item["fournisseur"] = fournisseur_nom.strip()

            yield item
