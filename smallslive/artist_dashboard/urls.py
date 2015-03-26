from django.conf.urls import patterns, include, url
from .views import MyGigsView


urlpatterns = patterns('artist_dashboard.views',
    url(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/edit/$', 'event_edit', name='event_edit'),
    url(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/$', 'event_detail', name='event_detail'),
    url(r'^edit-profile/$', 'edit_profile', name='edit_profile'),
    url(r'^my-gigs/$', 'my_gigs', name='my_gigs'),
    url(r'^$', 'dashboard', name='home'),
)
