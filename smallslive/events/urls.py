from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

urlpatterns = patterns('events.views',
    url(r'^live-stream-mezzrow/$', 'live_stream_mezzrow', name='live-stream-mezzrow'),
    url(r'^live-stream/$', 'live_stream', name='live-stream'),
    url(r'^new-popular/(?P<year>\d+)/(?P<month>\d+)/$',
        RedirectView.as_view(permanent=True, pattern_name='monthly_archive', query_string=True),
        name='monthly_archive_old'),
    url(r'^new-popular/$', RedirectView.as_view(permanent=True, pattern_name='archive', query_string=True),
        name='archive_old'),
    url(r'^calendar/(?P<year>\d+)/(?P<month>\d+)/$', 'monthly_schedule', name='monthly_schedule'),
    url(r'^calendar/$', 'schedule', name='schedule'),
    url(r'^schedule_carousel_ajax/(?P<pk>\d+)/$', 'schedule_carousel_ajax', name='schedule_carousel_ajax'),
    url(r'^event_carousel_ajax/$', 'event_carousel_ajax', name='event_carousel_ajax'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/$', 'event_detail', name='event_detail'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/clone/$', 'event_clone', name='event_clone'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/delete/$', 'event_delete', name='event_delete'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/edit/$', 'event_edit', name='event_edit'),
    url(r'^add/$', 'event_add', name='event_add'),
    url(r'^maintenance/$', 'maintenance_view', name='maintenance_view'),
)
