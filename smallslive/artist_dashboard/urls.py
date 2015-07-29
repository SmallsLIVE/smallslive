from django.conf.urls import patterns, include, url


urlpatterns = patterns('artist_dashboard.views',
    url(r'^toggle_recording_state/(?P<pk>\d+)/$', 'toggle_recording_state', name='recording_toggle'),
    url(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/edit/$', 'event_edit', name='event_edit'),
    url(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/metrics/$', 'event_metrics', name='event_metrics'),
    url(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/$', 'event_detail', name='event_detail'),
    url(r'^edit-profile/$', 'edit_profile', name='edit_profile'),
    url(r'^settings/$', 'artist_settings', name='settings'),
    url(r'^my-events/$', 'my_gigs', name='my_gigs'),
    url(r'^my-metrics/$', 'my_metrics', name='my_metrics'),
    url(r'^admin-metrics/$', 'admin_metrics', name='admin_metrics'),
    url(r'^legal-agreement/$', 'legal', name='legal'),
    url(r'^forgot-password/done/$', 'forgot_password_done', name='forgot_password_done'),
    url(r'^forgot-password/$', 'forgot_password', name='forgot_password'),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        'password_reset_from_key', name="reset_password_from_key"),
    url(r"^password/reset/done/$",
        'password_reset_from_key_done', name="reset_password_from_key_done"),
    url(r'^login/$', 'login', name='login'),
    url(r'^$', 'dashboard', name='home'),
)
