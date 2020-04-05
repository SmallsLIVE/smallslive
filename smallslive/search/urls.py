from django.conf.urls import patterns, include, url
import views


urlpatterns = patterns('search.views',
    url(r'^autocomplete/$', 'search_autocomplete', name='search_autocomplete'),
    url(r'^artist_form_autocomplete/$', 'artist_form_autocomplete', name='artist_form_autocomplete'),
    url(r'^archive/$', views.TemplateSearchView.as_view(), name='archive'),
    url(r'^$', views.TemplateSearchView.as_view(), name='search'),
    url(r'^ajax/search-bar/$', views.SearchBarView.as_view(), name='search-bar-ajax'),
    url(r'^ajax/artist-info/$', views.ArtistInfo.as_view(), name='artist-info-ajax'),
    url(r'^ajax/(?P<entity>[\w\-]+)/$', views.MainSearchView.as_view(), name='search-ajax'),
    url(r'^upcoming-ajax/', views.UpcomingSearchViewAjax.as_view(), name='calendar-search-ajax'),
)
