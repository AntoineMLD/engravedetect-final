# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FranceOptiqueItem(scrapy.Item):
    source_url = scrapy.Field()
    nom_verre = scrapy.Field()
    gravure_nasale = scrapy.Field()
    indice_verre = scrapy.Field()
    materiaux = scrapy.Field()
    fournisseur = scrapy.Field()
    pass
