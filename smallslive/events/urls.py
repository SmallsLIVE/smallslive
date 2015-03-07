from django.conf.urls import patterns, include, url


urlpatterns = patterns('events.views',
    url(r'^live-stream/$', 'live_stream', name='live-stream'),
    url(r'^schedule/(?P<year>\d+)/(?P<month>\d+)/$', 'monthly_schedule', name='monthly_schedule'),
    url(r'^schedule/$', 'schedule', name='schedule'),
    url(r'^event_carousel_ajax/$', 'event_carousel_ajax', name='event_carousel_ajax'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/$', 'event_detail', name='event_detail'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/clone/$', 'event_clone', name='event_clone'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/delete/$', 'event_delete', name='event_delete'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/edit/$', 'event_edit', name='event_edit'),
    url(r'^add/$', 'event_add', name='event_add'),
)
