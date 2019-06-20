from django.conf.urls import patterns, include, url

urlpatterns = patterns('subscriptions.views',
    url(r'^sync-payment-history/', 'sync_payment_history', name="sync_payment_history"),
    url(r'^email-list/', 'subscriber_list_emails', name="subscriber_list_emails"),
    url(r'^subscription-settings/', 'subscription_settings', name="subscription_settings"),
    url(r'^update-card/', 'update_card', name="update_card"),
    url(r'^upgrade-plan/(?P<plan_name>\w+)/', 'upgrade_plan', name="upgrade_plan"),
    url(r"^cancel/subscription/$", 'cancel_subscription',name="cancel_subscription"),
    url(r'^pledge-update/$', 'update_pledge', name="update_pledge"),
    url(r"^reactivate/subscription/$", 'reactivate_subscription',name="reactivate_subscription"),
    url(r'^payment-info/$', 'payment_info', name="payment_info"),
    url(r'^supporter/$', 'become_supporter', name="become_supporter"),
    url(r'^supporter/paypal-execute$', 'supporter_paypal_execute', name="supporter_paypal_execute"),
    url(r'^supporter/completed/$', 'become_supporter_complete', name="become_supporter_complete"),
    url(r'^donate/$', 'donate', name="donate"),
    url(r'^donate/completed/$', 'donate_complete', name="donate_complete"),
)
