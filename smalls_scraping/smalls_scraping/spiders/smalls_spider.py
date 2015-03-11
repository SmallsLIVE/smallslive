import arrow
import re
from datetime import datetime
from scrapy import Spider, Request
from smalls_scraping.items import SmallsEventItem


START_DATE = datetime(2014, 4, 1)
END_DATE = datetime(2014, 4, 1)


def remove_tags(text):
    TAG_RE = re.compile(r'</?a[^>]+>')
    return TAG_RE.sub('', text)


def generate_urls():
    urls = []
    for (date, _) in arrow.Arrow.span_range('day', START_DATE, END_DATE):
        url = "http://www.smallsjazzclub.com/indexnew.cfm?itemcategory=61473&calDate={d.month}/{d.day}/{d.year}".format(d=date)
        urls.append(url)
    return urls


class DmozSpider(Spider):
    name = "smalls"
    allowed_domains = ["smallsjazzclub.com"]
    start_urls = generate_urls()

    def parse(self, response):
        print "PARSING ITEM"
        response = response.replace(body=response.body.replace('<br>', '\n'))
        response = response.replace(body=remove_tags(response.body))
        date = response.xpath("//table//div[contains(@style,'text-align:center')]/text()").extract()[0]
        for sel in response.xpath("//td[@width='300']"):
            item = SmallsEventItem()

            item['date'] = date

            title = sel.xpath("font[contains(@style,'font-size:17px')]/text()").extract()[0]
            item['title'] = " ".join(title.split())

            time = sel.xpath("font[contains(@style,'font-size:16px')]/text()").extract()[0]
            start, end = time.split(" to ")
            item['start'] = start
            if end.count(" ") > 1:
                a, b, _ = end.split(" ", 2)
                end = " ".join([a, b])
            item['end'] = end

            for entry in sel.xpath('text()[normalize-space()]'):
                artists = re.split("\s{2,}", entry.extract().strip())
                artists = [tuple(artist.split(" - ")) for artist in artists]
            item['artists'] = artists
            yield item
