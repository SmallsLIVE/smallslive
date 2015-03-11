# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime


class EventDateTimePipeline(object):
    def process_item(self, item, spider):
        if item['start'].lower() == "midnight":
            item['start'] = "12:00 AM"
        start = "{0} {1}".format(item['date'], item['start'])

        start = datetime.datetime.strptime(start, "%A, %B %d, %Y %I:%M %p")
        if start.hour < 7:
            start += datetime.timedelta(days=1)
        item['start'] = start

        if item['end'].lower() == "close":
            item['end'] = "4:00 AM"
        end = "{0} {1}".format(item['date'], item['end'])
        end = datetime.datetime.strptime(end, "%A, %B %d, %Y %I:%M %p")
        if end.hour < 7:
            end += datetime.timedelta(days=1)
        item['end'] = end
        return item
