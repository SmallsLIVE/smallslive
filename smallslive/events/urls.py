from django.conf.urls import patterns, include, url


urlpatterns = patterns('events.views',
    url(r'^(?P<pk>\d+)/', 'event_detail', name='event_detail'),
    url(r'^add/', 'event_add', name='event_add'),
)
