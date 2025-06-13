import logging

import scrapy

from src.data.scraping.france_optique.items import FranceOptiqueItem


class GlassSpiderParticular(scrapy.Spider):
    name = "glass_spider_particular"
    allowed_domains = ["www.france-optique.com"]
    start_urls = ["https://www.france-optique.com/fournisseur/1488-hephilens"]

    def parse(self, response):
        self.log(f"Analyse de la page: {response.url}", level=logging.INFO)
        fournisseur_nom = (
            response.xpath("/html/body/div[2]/div/div[3]/div[2]/h2/text()").get()
            or response.xpath("/html/body/div[2]/div/div[3]/div/div/div/text()").get()
        )

        lines_container = response.xpath(
            '//div[contains(@class, "tableau_gravures") and contains(@class, "show-on-large") and contains(@class, "hide-on-med-and-down")]'
        )
        lines = lines_container.xpath('.//div[@class="row tr"]')

        for line in lines:
            item = FranceOptiqueItem()

            # Ajoute l'URL source à l'item
            item["source_url"] = response.url

            # Extraction du nom du verre
            nom_verre = line.xpath('.//div[contains(@class, "s3")]/p/text()').get()
            if not nom_verre.strip():
                continue
            item["nom_verre"] = nom_verre.strip()

            # Gravure nasale (gestion image ou texte)
            gravure_nasale_img = line.xpath('.//div[contains(@class, "s1")][2]/img/@src').get()
            gravure_nasale_txt = line.xpath('.//div[contains(@class, "s1")][2]/p[@class="gravure_txt"]/b/text()').get()
            if gravure_nasale_img:
                item["gravure_nasale"] = gravure_nasale_img
            elif gravure_nasale_txt:
                item["gravure_nasale"] = gravure_nasale_txt
            else:
                item["gravure_nasale"] = None

            # Extraction de l'indice et du matériau
            indice = line.xpath('.//div[contains(@class, "s1")][4]/p/text()').get()
            materiaux = line.xpath('.//div[contains(@class, "s1")][5]/p/text()').get()
            if not indice or not materiaux:
                continue
            item["indice"] = indice
            item["materiaux"] = materiaux

            # Ajout du nom du fournisseur de verre
            item["fournisseur"] = fournisseur_nom.strip()

            yield item
