from django.conf.urls import patterns, include, url


urlpatterns = patterns('institutional_subscriptions.views',
    url(r"^institutions/(?P<pk>\d+)/members/$", 'institution_members',
        name="institution_members"),
    url(r"^institutions/$", 'institution_list',
        name="institutions"),
)
