from django.conf.urls import patterns, include, url


urlpatterns = patterns('events.views',
    url(r'^calendar/$', 'calendar', name='calendar'),
    url(r'^my-gigs/$', 'my_gigs', name='my_gigs'),
    url(r'^recordings/$', 'recordings', name='recordings'),
    url(r'^musician-signup-choose-videos/$', 'artist_video_manager', name='artist_video_manager'),
    url(r'^dashboard/$', 'venue_dashboard', name='venue_dashboard'),
    url(r'^(?P<pk>\d+)-(?P<page_slug>[-\w]+)/$', 'event_detail', name='event_detail'),
    url(r'^(?P<pk>\d+)-(?P<page_slug>[-\w]+)/edit/$', 'event_edit', name='event_edit'),
    url(r'^add/$', 'event_add', name='event_add'),
)
