import logging

import scrapy

from src.data.scraping.france_optique.items import FranceOptiqueItem


class GlassSpiderOptovision(scrapy.Spider):
    name = "glass_spider_optovision"
    allowed_domains = ["www.france-optique.com"]
    start_urls = [
        "https://www.france-optique.com/gravures/fournisseur=789",
        "https://www.france-optique.com/gravures/fournisseur=2069",
        "https://www.france-optique.com/gravures/fournisseur=1407",
        "https://www.france-optique.com/gravures/fournisseur=2397",
        "https://www.france-optique.com/gravures/fournisseur=2644",
        "https://www.france-optique.com/gravures/fournisseur=2414",
    ]

    def parse(self, response):
        self.log(f"Analyse de la page: {response.url}", level=logging.INFO)
        fournisseur_nom = response.xpath(
            "/html/body/div[2]/div/div[3]/div/div/div/text()"
        ).get()

        lines = response.xpath(
            './/div[@class="tableau_gravures show-on-large hide-on-med-and-down"]/div'
        )

        for line in lines:

            item = FranceOptiqueItem()

            # Ajoute l'URL source à l'item
            item["source_url"] = response.url

            # Extraction du nom du verre
            glass_name = line.xpath(
                './/div[contains(@class, "td col s4 m4")]/p/text()'
            ).get()
            if not glass_name:
                continue
            item["nom_verre"] = glass_name

            # Gravure nasale (gestion image ou texte)
            gravure_nasale_img = line.xpath(
                './/div[contains(@class, "s1")][2]/img/@src'
            ).get()
            gravure_nasale_txt = line.xpath(
                './/div[contains(@class, "s1")][2]/p[@class="gravure_txt"]/b/text()'
            ).get()
            if gravure_nasale_img:
                item["gravure_nasale"] = gravure_nasale_img
            elif gravure_nasale_txt:
                item["gravure_nasale"] = gravure_nasale_txt
            else:
                item["gravure_nasale"] = None

            # Extraction de l'indice et du matériau
            glass_index = line.xpath('.//div[contains(@class, "s1")][4]/p/text()').get()

            material = line.xpath('.//div[contains(@class, "s1")][5]/p/text()').get()
            if not glass_index or not material:
                continue
            item["indice_verre"] = glass_index
            item["materiaux"] = material

            # Ajout du nom du fournisseur de verre
            item["fournisseur"] = fournisseur_nom.strip()

            yield item
