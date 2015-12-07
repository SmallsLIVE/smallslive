from django.conf.urls import patterns, include, url


urlpatterns = patterns('institutional_subscriptions.views',
    url(r"^institutions/$", 'institution_list',
        name="institutions"),
#    url(r"^media-redirect/(?P<recording_id>\d+)/$", 'media_redirect',
#        name="media_redirect"),
)
