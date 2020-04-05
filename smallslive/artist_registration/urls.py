from django.conf.urls import patterns, include, url
from .views import ActivateAccountRedirectView,  InviteArtistView


urlpatterns = patterns('artist_registration.views',
    url(r'^invite-artist/(?P<artist>\d+)/$', InviteArtistView.as_view(), name='invite_artist'),
    #url(r'^password-set/$', 'password_set', name='artist_registration_password_set'),
    # for backwards compatibility with older invitations
    url(r'^confirm-email/(?P<key>\w+)/$', 'artist_account_activate', name='artist_registration_confirm_email_old'),
    url(r'^activate-account/(?P<key>\w+)/$', ActivateAccountRedirectView.as_view(), name='artist_registration_confirm_email'),
    url(r'^activate-account-ajax/(?P<key>\w+)/$', 'artist_account_activate', name='artist_registration_confirm_email_ajax'),
)
