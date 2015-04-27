from django.conf.urls import patterns, include, url


urlpatterns = patterns('users.views',
    url(r"^confirm-email/(?P<key>\w+)/$", 'confirm_email',
        name="account_confirm_email"),
    url(r'^login/', 'login_view', name="accounts_login"),
    url(r'^user-settings/', 'user_settings_view', name="user_settings"),
    url(r'^signup/', 'signup_view', name="account_signup"),
    url(r'^', include('allauth.urls', app_name="allauth")),
)
