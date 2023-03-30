from django.urls import re_path, include
from django.conf.urls import  include, url
from artist_dashboard.views import *

app_name = 'artist_dashboard'

urlpatterns = [
    re_path(r'^toggle_recording_state/(?P<pk>\d+)/$', toggle_recording_state, name='recording_toggle'),
    re_path(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/edit/$', event_edit, name='event_edit'),
    re_path(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/edit-ajax/$', event_edit_ajax, name='event_edit_ajax'),
    re_path(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/metrics/$', event_metrics, name='event_metrics'),
    re_path(r'^event/(?P<pk>\d+)-(?P<slug>[-\w]+)/$', event_detail, name='event_detail'),
    re_path(r'^edit-profile/$', edit_profile, name='edit_profile'),
    re_path(r'^settings/$', artist_settings, name='settings'),
    re_path(r'^artist-payout-form/$', payout_form, name='payout_form'),
    re_path(r'^my-events/future/$', my_future_events, name='my_future_events'),
    re_path(r'^my-events/future/ajax$', my_future_events_ajax, name='my_future_events_ajax'),
    re_path(r'^my-events/past/$', my_past_events, name='my_past_events'),
    re_path(r'^my-events/past/ajax$', my_past_events_ajax, name='my_past_events_ajax'),
    re_path(r'^my-events/past/(?P<pk>\d+)$', my_past_events_info, name='my_past_events_info'),
    re_path(r'^my-payouts/(?P<pk>\d+)$', artist_payout_detail_ajax, name='my_payouts_ajax'),
    re_path(r'^admin-metrics-ajax/', metrics_ajax_display, name='metrics_ajax_display'),
    re_path(r'^my-metrics/$', metrics, name='metrics'),
    re_path(r'^previous-payouts/$', previous_payouts, name='previous_payouts'),
    re_path(r'^change-payout-period/$', change_payout_period, name='change_payout_period'),
    re_path(r'^admin-metrics/$', admin_metrics, name='admin_metrics'),
    re_path(r'^generate-payouts-range/$', metrics_payout_period, name='metrics_payout_period'),
    re_path(r'^generate-payouts/(?P<period_start>\d{4}-\d{2}-\d{2})/(?P<period_end>\d{4}-\d{2}-\d{2})/(?P<revenue>\d+)$', metrics_payout, name='metrics_payout'),
    re_path(r'^generate-payouts/$', metrics_payout, name='metrics_payout'),
    re_path(r'^poll-payouts/$', metrics_payout_poll, name='metrics_payout_poll'),
    re_path(r'^legal-agreement/$', legal, name='legal'),
    re_path(r'^forgot-password/done/$', forgot_password_done, name='forgot_password_done'),
    re_path(r'^forgot-password/$', forgot_password, name='forgot_password'),
    re_path(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        password_reset_from_key, name="reset_password_from_key"),
    re_path(r"^password/reset/done/$",
        password_reset_from_key_done, name="reset_password_from_key_done"),
    re_path(r'^$', login, name='login'),
    re_path(r'^$', dashboard, name='home')
]
