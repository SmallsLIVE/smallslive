from django.conf.urls import patterns, include, url
from .views import MyGigsView


urlpatterns = patterns('artist_dashboard.views',
    url(r'^edit-profile/$', 'edit_profile', name='dashboard_edit_profile'),
    url(r'^my-gigs/$', 'my_gigs', name='dashboard_my_gigs'),
    url(r'^$', 'dashboard', name='dashboard_home'),
)
