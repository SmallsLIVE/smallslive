from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView


admin.autodiscover()


class StaticPageView(TemplateView):
    def get_template_names(self):
        return ["{0}.html".format(self.kwargs['template_name'])]


urlpatterns = patterns('',
    url(r'^artists/', include('artists.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^static_page/(?P<template_name>[A-Za-z_-]*)/', StaticPageView.as_view(), name="static_page"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='home.html'), name="home"),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
