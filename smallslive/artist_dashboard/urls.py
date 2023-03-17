from django.urls import re_path, include
from django.conf.urls import  include, url
from artist_dashboard.views import *


urlpatterns = [
    url(r'^toggle_recording_state/(?P<pk>\d+)/$', toggle_recording_state, name='recording_toggle'),
    url(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/edit/$', event_edit, name='event_edit'),
    url(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/edit-ajax/$', event_edit_ajax, name='event_edit_ajax'),
    url(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/metrics/$', event_metrics, name='event_metrics'),
    url(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/$', event_detail, name='event_detail'),
    url(r'^edit-profile/$', edit_profile, name='edit_profile'),
    url(r'^settings/$', artist_settings, name='settings'),
    url(r'^artist-payout-form/$', payout_form, name='payout_form'),
    url(r'^my-events/future/$', my_future_events, name='my_future_events'),
    url(r'^my-events/future/ajax$', my_future_events_ajax, name='my_future_events_ajax'),
    url(r'^my-events/past/$', my_past_events, name='my_past_events'),
    url(r'^my-events/past/ajax$', my_past_events_ajax, name='my_past_events_ajax'),
    url(r'^my-events/past/(?P<pk>\d+)$', my_past_events_info, name='my_past_events_info'),
    url(r'^my-payouts/(?P<pk>\d+)$', artist_payout_detail_ajax, name='my_payouts_ajax'),
    url(r'^admin-metrics-ajax/', metrics_ajax_display, name='metrics_ajax_display'),
    url(r'^my-metrics/$', metrics, name='metrics'),
    url(r'^previous-payouts/$', previous_payouts, name='previous_payouts'),
    url(r'^change-payout-period/$', change_payout_period, name='change_payout_period'),
    url(r'^admin-metrics/$', admin_metrics, name='admin_metrics'),
    url(r'^generate-payouts-range/$', metrics_payout_period, name='metrics_payout_period'),
    url(r'^generate-payouts/(?P<period_start>\d{4}-\d{2}-\d{2})/(?P<period_end>\d{4}-\d{2}-\d{2})/(?P<revenue>\d+)$', metrics_payout, name='metrics_payout'),
    url(r'^generate-payouts/$', metrics_payout, name='metrics_payout'),
    url(r'^poll-payouts/$', metrics_payout_poll, name='metrics_payout_poll'),
    url(r'^legal-agreement/$', legal, name='legal'),
    url(r'^forgot-password/done/$', forgot_password_done, name='forgot_password_done'),
    url(r'^forgot-password/$', forgot_password, name='forgot_password'),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        password_reset_from_key, name="reset_password_from_key"),
    url(r"^password/reset/done/$",
        password_reset_from_key_done, name="reset_password_from_key_done"),
    url(r'^$', login, name='login'),
    url(r'^$', dashboard, name='home')
]
