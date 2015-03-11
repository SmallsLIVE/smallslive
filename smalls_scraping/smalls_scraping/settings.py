# -*- coding: utf-8 -*-

# Scrapy settings for smalls_scraping project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import sys
sys.path.append('/Users/bezidejni/Documents/projekti/GitHub/appsembler/smallslive/smallslive')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'smallslive.settings.local_filip'

BOT_NAME = 'smalls_scraping'

SPIDER_MODULES = ['smalls_scraping.spiders']
NEWSPIDER_MODULE = 'smalls_scraping.spiders'
ITEM_PIPELINES = {
    'smalls_scraping.pipelines.EventDateTimePipeline': 300,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'smalls_scraping (+http://www.yourdomain.com)'

DOWNLOAD_DELAY = 0.35
