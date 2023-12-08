from django.conf.urls import include, url
from django.urls import reverse
from .views import *


urlpatterns = [
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/edit/$', artist_edit, name='artist_edit'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/$', artist_detail, name='artist_detail'),
    url(r'^(?P<pk>\d+)/instrument_ajax/$', artist_instrument_ajax, name='artist_intrument_ajax'),
    url(r'^add/$', artist_add, name='artist_add'),
    url(r'^emails$', artist_list_emails, name='artist_list_emails'),
    url(r'^$', artist_list, name='artist_list'),
    url(r'^download-artist-csv/$', download_artist_list_csv, name='download_artist_list_csv')
]
