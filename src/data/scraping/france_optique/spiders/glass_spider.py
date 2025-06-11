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
        fournisseur_nom = response.xpath(
            "/html/body/div[2]/div/div[3]/div[2]/h2/text()"
        ).get()
        self.log(f"Fournisseur trouvé: {fournisseur_nom}", level=logging.INFO)

        lines = response.xpath('//*[@id="gravures"]/div[2]//div')
        self.log(f"Nombre de lignes trouvées: {len(lines)}", level=logging.INFO)

        for line in lines:
            item = FranceOptiqueItem()

            # Ajoute l'URL source à l'item
            item["source_url"] = response.url

            # Extraction du nom du verre
            nom_verre = line.css(
                "div.row.tr:not(.group) div.td.col.s3.m3 p::text"
            ).get("")
            if not nom_verre.strip():
                self.log("Ligne ignorée: nom de verre vide", level=logging.DEBUG)
                continue
            item["nom_verre"] = nom_verre.strip()
            self.log(f"Nom du verre trouvé: {nom_verre.strip()}", level=logging.DEBUG)

            # Extraction de la gravure nasale
            gravure_nasale = line.xpath(
                './/div[contains(@class, "td")][2]//p[@class="gravure_txt"]/b/text()'
            ).get()
            gravure_nasale = (
                gravure_nasale
                or line.xpath(
                    './/div[contains(@class, "td")][2]/img[contains(@src, "nasal")]/@src'
                ).get()
            )
            if not gravure_nasale:
                self.log("Ligne ignorée: gravure nasale non trouvée", level=logging.DEBUG)
                continue
            item["gravure_nasale"] = gravure_nasale
            self.log(f"Gravure nasale trouvée: {gravure_nasale}", level=logging.DEBUG)

            # Extraction de l'indice et du matériau
            indice_verre = line.css(
                "div.row.tr:not(.group) div.td.col.s1.m1 p::text"
            ).get()
            materiaux = line.css("div.td.col.s2.m2 p::text").get()
            if not indice_verre or not materiaux:
                self.log("Ligne ignorée: indice ou matériau manquant", level=logging.DEBUG)
                continue
            item["indice_verre"] = indice_verre
            item["materiaux"] = materiaux
            self.log(f"Indice: {indice_verre}, Matériau: {materiaux}", level=logging.DEBUG)

            # Ajout du nom du fournisseur de verre
            item["fournisseur"] = fournisseur_nom.strip()

            self.log(f"Item complet généré: {item}", level=logging.INFO)
            yield item
