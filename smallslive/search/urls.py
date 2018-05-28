from django.conf.urls import patterns, include, url
import views


urlpatterns = patterns('search.views',
    url(r'^autocomplete/$', 'search_autocomplete', name='search_autocomplete'),
    url(r'^$', views.GlobalSearchView.as_view(), name='search'),
    url(r'^get-artists/$', views.get_artists, name='get_artists'),
)
