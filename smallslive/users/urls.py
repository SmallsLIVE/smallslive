from django.conf.urls import patterns, include, url

urlpatterns = patterns('users.views',
    url(r'^admin_email/$', 'admin_email_confirmation', name="admin_email_confirmation"),
    url(r"^confirm-email/(?P<key>\w+)/$", 'confirm_email',
        name="account_confirm_email"),
    url(r'^login/', 'login_view', name="accounts_login"),
    url(r'^user-settings/', 'user_settings_view', name="user_settings"),
    url(r'^settings/', 'user_settings_view_new', name="user_settings_new"),
    url(r'^tax-letter/', 'user_tax_letter', name="user_tax_letter"),
    url(r'^tax-letter-html/', 'user_tax_letter_html', name="user_tax_letter_html"),
    url(r'^signup/complete/', 'signup_complete', name="accounts_signup_complete"),
    url(r'^signup/(?P<plan_name>\w+)/', 'signup_view', name="accounts_signup"),
    url(r'^signup/', 'signup_landing', name="signup_landing"),
    url(r'^', include('allauth.urls', app_name="allauth")),
)
