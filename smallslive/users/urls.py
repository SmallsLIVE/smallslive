from django.conf.urls import patterns, include, url


urlpatterns = patterns('users.views',
    url(r"^confirm-email/(?P<key>\w+)/$", 'confirm_email',
        name="account_confirm_email"),
    url(r'^login/', 'login_view', name="accounts_login"),
    url(r'^user-settings/', 'user_settings_view', name="user_settings"),
    url(r'^signup/payment/', 'signup_payment', name="accounts_signup_payment"),
    url(r'^signup/(?P<plan_name>\w+)/', 'signup_view', name="accounts_signup"),
    url(r'^signup/', 'signup_landing', name="signup_landing"),
    url(r'^', include('allauth.urls', app_name="allauth")),
)
