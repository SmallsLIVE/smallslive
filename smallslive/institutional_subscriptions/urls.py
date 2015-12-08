from django.conf.urls import patterns, include, url


urlpatterns = patterns('institutional_subscriptions.views',
    url(r"^(?P<pk>\d+)/members/$", 'institution_members',
        name="institution_members"),
    url(r"^add/$", 'institution_add',
        name="institution_add"),
    url(r"^$", 'institution_list',
        name="institutions"),
)
