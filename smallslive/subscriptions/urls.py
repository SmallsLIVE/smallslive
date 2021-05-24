from django.conf.urls import patterns, include, url

urlpatterns = patterns('subscriptions.views',
    url(r'^sync-payment-history/', 'sync_payment_history', name='sync_payment_history'),
    url(r'^email-list/', 'subscriber_list_emails', name='subscriber_list_emails'),
    url(r'^update-card/', 'update_card', name='update_card'),
    url(r'^cancel/subscription/$', 'cancel_subscription',name='cancel_subscription'),
    url(r'^pledge-update/$', 'update_pledge', name='update_pledge'),
    url(r'^reactivate/subscription/$', 'reactivate_subscription',name='reactivate_subscription'),
    url(r'^payment-info/$', 'payment_info', name='payment_info'),
    url(r'^donation-preview/$', 'donation_preview', name='donation_preview'),
    url(r'^supporter/$', 'become_supporter', name='become_supporter'),
    url(r'^event-sponsorship/$', 'event_sponsorship', name='event_sponsorship'),
    url(r'^product-support/(?P<product_id>[-\d]+)$', 'product_support', name='product_support'),
    url(r'^tickets/$', 'ticket_support', name='ticket_support'),
    url(r'^supporter/paypal-execute$', 'supporter_paypal_execute', name='supporter_paypal_execute'),
    url(r'^supporter/completed/$', 'become_supporter_complete', name='become_supporter_complete'),
    url(r'^donate/$', 'donate', name='donate'),
    url(r'^supporter/pending', 'supporter_pending', name='supporter_pending'),
    url(r'^supporters-export', 'supporter_list_export', name='supporter_list_export'),
    url(r'^supporters/$', 'supporter_list', name='supporter_list'),
    url(r'^sponsors/$', 'sponsor_list', name='sponsor_list'),
)
