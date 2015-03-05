from django.conf.urls import patterns, include, url


urlpatterns = patterns('search.views',
    url(r'^autocomplete/$', 'search_autocomplete', name='search_autocomplete'),
)
