from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

admin.autodiscover()


class StaticPageView(TemplateView):
    def get_template_names(self):
        return ["{0}.html".format(self.kwargs['template_name'])]


urlpatterns = patterns('',
    url(r'^static_page/(?P<template_name>[A-Za-z_-]*)/', StaticPageView.as_view(), name="static_page"),
    url(r'^admin/', include(admin.site.urls)),
)
