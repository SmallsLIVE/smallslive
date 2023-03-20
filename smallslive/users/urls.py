from django.urls import path, re_path, include
from users.views import *

urlpatterns = [
    path(r'^admin_email/$', admin_email_confirmation, name="admin_email_confirmation"),
    path(r'^email-confirmed/$', email_confirmed,
        name="email_confirmed"),
    path(r'^email-confirm-ajax/$', email_confirm_resend_ajax,
        name="email_confirm_resend_ajax"),
    path(r'^email-confirmed-donate/$', email_confirmed_donate,
        name="email_confirmed_donate"),
    path(r'^email-confirmed-catalog/$', email_confirmed_catalog,
        name="email_confirmed_catalog"),
    path(r'^login/', login_view, name="accounts_login"),
    path(r'^user-settings/', user_settings_view, name="user_settings"),
    path(r'^settings/', user_settings_view_new, name="user_settings_new"),
    path(r'^tax-letter/', user_tax_letter, name="user_tax_letter"),
    path(r'^tax-letter-html/', user_tax_letter_html, name="user_tax_letter_html"),
    path(r'^signup/complete/', signup_complete, name="accounts_signup_complete"),
    path(r'^signup/(?P<plan_name>\w+)/', signup_view, name="accounts_signup"),
    path(r'^signup/', signup_landing, name="signup_landing"),
    path(r'^check-account-status/', check_account_status, name='check_account_status'),
    path(r'^', include('allauth.urls'), name='allauth'),
]
