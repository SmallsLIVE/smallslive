from django.conf.urls import url, include

from oscar.core.application import Application
from oscar.core.loading import get_class
from oscar.apps.catalogue.reviews.app import application as reviews_app
from oscar.apps.catalogue.app import BaseCatalogueApplication
from oscar_apps.catalogue.views import ArtistCatalogue


class BaseCatalogueApplication(BaseCatalogueApplication):

    def get_urls(self):
        urlpatterns = super(BaseCatalogueApplication, self).get_urls()
        urlpatterns += [
            url(r'^/artist-catalogue/', ArtistCatalogue.as_view(), name='artist_store'),
            ]
        return self.post_process_urls(urlpatterns)