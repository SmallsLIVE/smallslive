from django.conf.urls import include, url
from django.urls import re_path
from .views import ActivateAccountRedirectView,  InviteArtistView, artist_account_activate


urlpatterns = [
    url(r'^invite-artist/(?P<artist>\d+)/$', InviteArtistView.as_view(), name='invite_artist'),
    #url(r'^password-set/$', 'password_set', name='artist_registration_password_set'),
    # for backwards compatibility with older invitations
    url(r'^confirm-email/(?P<key>\w+)/$', artist_account_activate, name='artist_registration_confirm_email_old'),
    url(r'^activate-account/(?P<key>\w+)/$', ActivateAccountRedirectView.as_view(), name='artist_registration_confirm_email'),
    url(r'^activate-account-ajax/(?P<key>\w+)/$', artist_account_activate, name='artist_registration_confirm_email_ajax'),
]
