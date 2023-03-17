from django.conf.urls import include, url
from .views import *


urlpatterns = [
    url(r'^autocomplete/$', search_autocomplete, name='search_autocomplete'),
    url(r'^artist_form_autocomplete/$', artist_form_autocomplete, name='artist_form_autocomplete'),
    url(r'^archive/$', TemplateSearchView.as_view(), name='archive'),
    url(r'^$', TemplateSearchView.as_view(), name='search'),
    url(r'^ajax/search-bar/$', SearchBarView.as_view(), name='search-bar-ajax'),
    url(r'^ajax/artist-info/$', ArtistInfo.as_view(), name='artist-info-ajax'),
    url(r'^ajax/(?P<entity>[\w\-]+)/$', MainSearchView.as_view(), name='search-ajax'),
    url(r'^upcoming-ajax/', UpcomingSearchViewAjax.as_view(), name='calendar-search-ajax'),
]
