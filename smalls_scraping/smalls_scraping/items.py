# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.contrib.djangoitem import DjangoItem


class SmallsEventItem(DjangoItem):
    title = scrapy.Field()
    date = scrapy.Field()
    start = scrapy.Field()
    end = scrapy.Field()
    artists = scrapy.Field()
