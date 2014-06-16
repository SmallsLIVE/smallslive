from django.conf.urls import patterns, include, url


urlpatterns = patterns('events.views',
    url(r'^calendar/$', 'calendar', name='calendar'),
    url(r'^my-gigs/$', 'my_gigs', name='my_gigs'),
    url(r'^video-manager/$', 'video_manager', name='video_manager'),
    url(r'^dashboard/$', 'venue_dashboard', name='venue_dashboard'),
    url(r'^(?P<pk>\d+)/$', 'event_detail', name='event_detail'),
    url(r'^(?P<pk>\d+)/edit/$', 'event_edit', name='event_edit'),
    url(r'^add/$', 'event_add', name='event_add'),
)
