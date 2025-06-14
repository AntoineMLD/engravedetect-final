# Scrapy settings for france_optique project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

BOT_NAME = "france_optique"

SPIDER_MODULES = ["src.data.scraping.france_optique.spiders"]
NEWSPIDER_MODULE = "src.data.scraping.france_optique.spiders"

FEED_EXPORT_ENCODING = "utf-8"

# Configuration de la base de données
SQLALCHEMY_DATABASE_URI = (
    f"mssql+pyodbc://{os.getenv('AZURE_USERNAME')}:{os.getenv('AZURE_PASSWORD')}@"
    f"{os.getenv('AZURE_SERVER')}/{os.getenv('AZURE_DATABASE')}?"
    "driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

# Paramètres de scraping optimisés
CONCURRENT_REQUESTS = 1  # Limite le nombre de requêtes simultanées
DOWNLOAD_DELAY = 3  # Ajoute un délai de 3 secondes entre les requêtes
RANDOMIZE_DOWNLOAD_DELAY = True

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 5  # Nombre de tentatives
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Configure maximum concurrent requests performing to the same domain
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "france_optique (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    "src.data.scraping.france_optique.middlewares.FranceOptiqueSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
    "src.data.scraping.france_optique.middlewares.FranceOptiqueDownloaderMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
ITEM_PIPELINES = {
    "src.data.scraping.france_optique.pipelines.AzureSQLPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"
