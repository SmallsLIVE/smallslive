from django.conf.urls import include, url
from oscar.apps.catalogue import apps
from oscar.core.loading import get_class



class CatalogueConfig(apps.CatalogueConfig):
    label = 'catalogue'
    name = 'oscar_apps.catalogue'
    verbose_name = 'Catalogue'

    namespace = 'catalogue'

    def ready(self):
        # from . import receivers  # noqa

        super().ready()

        self.detail_view = get_class('catalogue.views', 'ProductDetailView')
        self.catalogue_view = get_class('catalogue.views', 'CatalogueView')
        self.category_view = get_class('catalogue.views', 'ProductCategoryView')
        self.range_view = get_class('offer.views', 'RangeDetailView')

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(r'^$', self.catalogue_view.as_view(), name='index'),
            url(r'^(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                self.detail_view.as_view(), name='detail'),
            url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)_(?P<pk>\d+)/$',
                self.category_view.as_view(), name='category'),
            url(r'^ranges/(?P<slug>[\w-]+)/$',
                self.range_view.as_view(), name='range'),
        ]
        return self.post_process_urls(urls)

