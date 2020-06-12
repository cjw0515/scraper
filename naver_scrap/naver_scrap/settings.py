# -*- coding: utf-8 -*-

# Scrapy settings for naver_scrap project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import sys, os
sys.path.append("C:/anaconda3/envs/scraper-10x10/Lib/site-packages")
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
BOT_NAME = 'naver_scrap'

SPIDER_MODULES = ['naver_scrap.spiders']
NEWSPIDER_MODULE = 'naver_scrap.spiders'

# ITEM_PIPELINES = {
#    'naver_scrap.pipelines.NaverScrapPipeline': 300,
# }

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

BUCKET_NAME = 'bi-temp'
BUCKET_PREFIX = 'datalake/crawling/'

# LOG_LEVEL = 'ERROR'
LOG_LEVEL = 'INFO'

# FEEDS = {
#     's3://bi-temp/datalake/crawling/test.json': {
#         'format': 'json',
#         'encoding': 'utf8',
#         'store_empty': False,
#         'fields': None,
#         'indent': 4,
#     },
#     'item.json': {
#         'format': 'json',
#         'encoding': 'utf8',
#         'store_empty': False,
#         'fields': None,
#         'indent': 4,
#     },
#     # '/home/user/documents/items.xml': {
#     #     'format': 'xml',
#     #     'fields': ['name', 'price'],
#     #     'encoding': 'latin1',
#     #     'indent': 8,
#     # },
#     # pathlib.Path('items.csv'): {
#     #     'format': 'csv',
#     #     'fields': ['price', 'name'],
#     # },
# }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'naver_scrap (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   'naver_scrap.middlewares.NaverScrapSpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'naver_scrap.middlewares.NaverScrapDownloaderProxyMiddleware': 543,
   'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# # The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# # The maximum download delay to be set in case of high latencies
# #AUTOTHROTTLE_MAX_DELAY = 60
# # The average number of requests Scrapy should be sending in parallel to
# # each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
