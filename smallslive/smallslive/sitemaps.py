from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps import GenericSitemap
from django.urls import reverse
from artists.models import Artist
from events.models import Event
from oscar_apps.catalogue.models import Product

artist_dict = {
    'queryset': Artist.objects.all(),
    'changefreq': 'weekly'
}

event_dict = {
    'queryset': Event.objects.all(),
    'date_field': 'modified',
    'changefreq': 'never'
}

product_dict = {
    'queryset': Product.objects.browsable(),
    'date_field': 'date_updated',
    'changefreq': 'never'
}

class StaticSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return [
            'institutions',
            'contact-and-info',
            'revenue-share',
            'terms-and-conditions',
            'about-us',
            'photo-gallery',
            'newsletters',
            'signup_landing',
            'accounts_login'
        ]

    def location(self, item):
        return reverse(item)


class DailyChangingSitemap(Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return [
            'home',
            'live-stream',
            'schedule',
            'archive',
            'promotions:home'
        ]

    def location(self, item):
        return reverse(item)


sitemaps = {
    'artists': GenericSitemap(artist_dict, priority=0.6, changefreq='weekly'),
    'events': GenericSitemap(event_dict, priority=0.5, changefreq='never'),
    'products': GenericSitemap(product_dict, priority=0.4, changefreq='never'),
    'static': StaticSitemap,
    'daily_static': DailyChangingSitemap,
}
