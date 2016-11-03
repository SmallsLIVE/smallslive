from django.conf.urls import patterns, include, url


urlpatterns = patterns('users.views',
    url(r'^admin_email/$', 'admin_email_confirmation', name="admin_email_confirmation"),
    url(r"^confirm-email/(?P<key>\w+)/$", 'confirm_email',
        name="account_confirm_email"),
    url(r'^login/', 'login_view', name="accounts_login"),
    url(r'^sync-payment-history/', 'sync_payment_history', name="sync_payment_history"),
    url(r'^email-list/', 'subscriber_list_emails', name="subscriber_list_emails"),
    url(r'^user-settings/', 'user_settings_view', name="user_settings"),
    url(r'^subscription-settings/', 'subscription_settings', name="subscription_settings"),
    url(r'^update-card/', 'update_card', name="update_card"),
    url(r'^upgrade-plan/(?P<plan_name>\w+)/', 'upgrade_plan', name="upgrade_plan"),
    url(r"^cancel/subscription/$", 'cancel_subscription',name="cancel_subscription"),
    url(r"^reactivate/subscription/$", 'reactivate_subscription',name="reactivate_subscription"),
    url(r'^signup/complete/', 'signup_complete', name="accounts_signup_complete"),
    url(r'^signup/(?P<plan_name>\w+)/payment/', 'signup_payment', name="accounts_signup_payment"),
    url(r'^signup/(?P<plan_name>\w+)/', 'signup_view', name="accounts_signup"),
    url(r'^signup/', 'signup_landing', name="signup_landing"),
    url(r'^', include('allauth.urls', app_name="allauth")),
)
