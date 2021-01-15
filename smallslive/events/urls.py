from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

urlpatterns = patterns('events.views',
    url(r'^live-stream-mezzrow/$', RedirectView.as_view(url='/', permanent=True), name='live-stream-mezzrow'),
    url(r'^live-stream/$', RedirectView.as_view(url='/', permanent=True), name='live-stream'),
    url(r'^new-popular/(?P<year>\d+)/(?P<month>\d+)/$',
        RedirectView.as_view(permanent=True, pattern_name='monthly_archive', query_string=True),
        name='monthly_archive_old'),
    url(r'^new-popular/$', RedirectView.as_view(permanent=True, pattern_name='archive', query_string=True),
        name='archive_old'),
    url(r'^calendar/$', 'schedule', name='schedule'),
    url(r'^schedule_carousel_ajax/(?P<pk>\d+)/$', 'schedule_carousel_ajax', name='schedule_carousel_ajax'),
    url(r'^event_carousel_ajax/$', 'event_carousel_ajax', name='event_carousel_ajax'),
    url(r'^event_popular_ajax/$', 'event_popular_ajax', name='event_popular_ajax'),
    url(r'^redirect/(?P<pk>\d+)/$', 'event_detail_redirect', name='event_detail_redirect'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/$', 'event_detail', name='event_detail'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/comments/$', 'event_comments', name='event_comments'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/clone/$', 'event_clone', name='event_clone'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/delete/$', 'event_delete', name='event_delete'),
    url(r'^(?P<pk>\d+)-(?P<slug>[-\w]+)/edit/$', 'event_edit', name='event_edit'),
    url(r'^(?P<pk>\d+)/update-metrics/$', 'event_update_metrics', name='event_update_metrics'),
    url(r'^add/$', 'event_add', name='event_add'),
    url(r'^(?P<pk>\d+)/publish/$', 'publish_event', name='publish_event'),
    url(r'^event_counts/', 'metrics_event_counts', name='event_counts'),
    url(r'^remove_comment/$', 'remove_comment', name='remove_comment'),

    # venue
    url(r'^add_venue/$', 'venue_add', name='venue_add'),
    url(r'^edit_venue/(?P<pk>\d+)/$', 'venue_edit', name='venue_edit'),

    # maintenance
    url(r'^maintenance/$', 'maintenance_view', name='maintenance_view'),
)
