from django.conf.urls import patterns, include, url


urlpatterns = patterns('artist_registration.views',
    url(r'^password-set/$', 'password_set', name='artist_registration_password_set'),
    url(r'^confirm-email/(?P<key>\w+)/$', 'confirm_email', name='artist_registration_confirm_email'),
)
