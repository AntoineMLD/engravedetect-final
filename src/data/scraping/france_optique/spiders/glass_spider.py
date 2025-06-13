import logging

import scrapy

from src.data.scraping.france_optique.items import FranceOptiqueItem


class GlassSpider(scrapy.Spider):
    name = "glass_spider"
    allowed_domains = ["www.france-optique.com"]
    start_urls = [
        "https://www.france-optique.com/fournisseur/1344-bbgr-optique/gravures",
        "https://www.france-optique.com/fournisseur/2399-adn-optis",
    ]

    def parse(self, response):
        self.log(f"Analyse de la page: {response.url}", level=logging.INFO)
        fournisseur_nom = response.xpath("/html/body/div[2]/div/div[3]/div[2]/h2/text()").get()

        lines = response.xpath('//*[@id="gravures"]/div[2]//div')

        for line in lines:
            item = FranceOptiqueItem()

            # Ajoute l'URL source à l'item
            item["source_url"] = response.url

            # Extraction du nom du verre
            nom_verre = line.css("div.row.tr:not(.group) div.td.col.s3.m3 p::text").get("")
            if not nom_verre.strip():
                continue
            item["nom_verre"] = nom_verre.strip()

            # Extraction de la gravure nasale
            gravure_nasale = line.xpath('.//div[contains(@class, "td")][2]//p[@class="gravure_txt"]/b/text()').get()
            gravure_nasale = (
                gravure_nasale or line.xpath('.//div[contains(@class, "td")][2]/img[contains(@src, "nasal")]/@src').get()
            )
            if not gravure_nasale:
                continue
            item["gravure_nasale"] = gravure_nasale

            # Extraction de l'indice et du matériau
            indice = line.css("div.row.tr:not(.group) div.td.col.s1.m1 p::text").get()
            materiaux = line.css("div.td.col.s2.m2 p::text").get()
            if not indice or not materiaux:
                continue
            item["indice"] = indice
            item["materiaux"] = materiaux

            # Ajout du nom du fournisseur de verre
            item["fournisseur"] = fournisseur_nom.strip()

            yield item
