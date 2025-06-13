# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FranceOptiqueItem(scrapy.Item):
    source_url = scrapy.Field()
    nom_verre = scrapy.Field()
    gravure_nasale = scrapy.Field()
    indice = scrapy.Field()
    materiaux = scrapy.Field()
    fournisseur = scrapy.Field()
    image_gravure = scrapy.Field()  # Chemin vers l'image sauvegardée
