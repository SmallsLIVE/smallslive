from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

import djstripe

# uncomment these lines to enable the Djrill admin interface 
#from djrill import DjrillAdminSite
#admin.site = DjrillAdminSite()

admin.autodiscover()


class StaticPageView(TemplateView):
    def get_template_names(self):
        return ["{0}.html".format(self.kwargs['template_name'])]


urlpatterns = patterns('',
    url(r'^artists/', include('artists.urls', app_name="artists")),
    url(r'^events/', include('events.urls', app_name="events")),
    url(r'^static_page/(?P<template_name>[A-Za-z_-]*)/$', StaticPageView.as_view(), name="static_page"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls', app_name="allauth")),
    url(r'^subscription/', include('subscription.urls', namespace='subscription')),
    url(r'^payments/', include('djstripe.urls', namespace="djstripe")),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', 'events.views.homepage', name="home"),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
