from django.conf.urls import patterns, include, url


urlpatterns = patterns('artists.views',
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/edit/$', 'artist_edit', name='artist_edit'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/$', 'artist_detail', name='artist_detail'),
    url(r'^(?P<pk>\d+)/instrument_ajax/$', 'artist_instrument_ajax', name='artist_intrument_ajax'),
    url(r'^add/$', 'artist_add', name='artist_add'),
)
