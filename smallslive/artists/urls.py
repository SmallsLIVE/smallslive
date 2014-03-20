from django.conf.urls import patterns, include, url


urlpatterns = patterns('artists.views',
    url(r'^(?P<pk>\d+)/', 'artist_detail', name='artist_detail'),
    url(r'^add/', 'artist_add', name='artist_add'),
)
