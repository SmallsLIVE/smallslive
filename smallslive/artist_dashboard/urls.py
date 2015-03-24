from django.conf.urls import patterns, include, url
from .views import MyGigsView


urlpatterns = patterns('artist_dashboard.views',
    url(r'^my-gigs/$', 'my_gigs', name='dashboard_my_gigs'),
)
