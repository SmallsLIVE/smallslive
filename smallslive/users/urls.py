from django.conf.urls import patterns, include, url

urlpatterns = patterns('users.views',
    url(r'^admin_email/$', 'admin_email_confirmation', name="admin_email_confirmation"),
    url(r'^email-confirmed/$', 'email_confirmed',
        name="email_confirmed"),
    url(r'^email-confirm-ajax/$', 'email_confirm_resend_ajax',
        name="email_confirm_resend_ajax"),
    url(r'^email-confirmed-donate/$', 'email_confirmed_donate',
        name="email_confirmed_donate"),
    url(r'^email-confirmed-catalog/$', 'email_confirmed_catalog',
        name="email_confirmed_catalog"),
    url(r'^login/', 'login_view', name="accounts_login"),
    url(r'^user-settings/', 'user_settings_view', name="user_settings"),
    url(r'^settings/', 'user_settings_view_new', name="user_settings_new"),
    url(r'^tax-letter/', 'user_tax_letter', name="user_tax_letter"),
    url(r'^tax-letter-html/', 'user_tax_letter_html', name="user_tax_letter_html"),
    url(r'^signup/complete/', 'signup_complete', name="accounts_signup_complete"),
    url(r'^signup/(?P<plan_name>\w+)/', 'signup_view', name="accounts_signup"),
    url(r'^signup/', 'signup_landing', name="signup_landing"),
    url(r'^check-account-status/', 'check_account_status', name='check_account_status'),
    url(r'^', include('allauth.urls', app_name="allauth")),
)
