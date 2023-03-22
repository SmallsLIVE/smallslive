from django.urls import path, re_path, include
from users.views import *

urlpatterns = [
    re_path(r'^admin_email/$', admin_email_confirmation, name="admin_email_confirmation"),
    re_path(r'^email-confirmed/$', email_confirmed,
        name="email_confirmed"),
    re_path(r'^email-confirm-ajax/$', email_confirm_resend_ajax,
        name="email_confirm_resend_ajax"),
    re_path(r'^email-confirmed-donate/$', email_confirmed_donate,
        name="email_confirmed_donate"),
    re_path(r'^email-confirmed-catalog/$', email_confirmed_catalog,
        name="email_confirmed_catalog"),
    re_path(r'^login/', login_view, name="accounts_login"),
    re_path(r'^user-settings/', user_settings_view, name="user_settings"),
    re_path(r'^settings/', user_settings_view_new, name="user_settings_new"),
    re_path(r'^tax-letter/', user_tax_letter, name="user_tax_letter"),
    re_path(r'^tax-letter-html/', user_tax_letter_html, name="user_tax_letter_html"),
    re_path(r'^signup/complete/', signup_complete, name="accounts_signup_complete"),
    re_path(r'^signup/(?P<plan_name>\w+)/', signup_view, name="accounts_signup"),
    re_path(r'^signup/', signup_landing, name="signup_landing"),
    re_path(r'^check-account-status/', check_account_status, name='check_account_status'),
    re_path(r'^', include('allauth.urls'), name='allauth'),
]
