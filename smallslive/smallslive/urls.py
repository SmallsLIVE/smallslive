from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from oscar.app import application

# uncomment these lines to enable the Djrill admin interface 
#from djrill import DjrillAdminSite
#admin.site = DjrillAdminSite()

admin.autodiscover()


class StaticPageView(TemplateView):
    def get_template_names(self):
        return ["{0}.html".format(self.kwargs['template_name'])]


urlpatterns = patterns('',
    url(r'^artist-registration/', include('artist_registration.urls', app_name="artist_registration")),
    url(r'^artists/', include('artists.urls', app_name="artists")),
    url(r'^events/', include('events.urls', app_name="events")),
    url(r'^static_page/(?P<template_name>[A-Za-z_-]*)/$', StaticPageView.as_view(), name="static_page"),
    url(r'^admin/', include(admin.site.urls)),
    url(r"^accounts/confirm-email/(?P<key>\w+)/$", 'users.views.confirm_email',
        name="account_confirm_email"),
    url(r'^accounts/user-settings/', 'users.views.user_settings_view', name="user_settings"),
    url(r'^accounts/signup/', 'users.views.signup_view', name="account_signup"),
    url(r'^accounts/', include('allauth.urls', app_name="allauth")),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^search/artist/', 'artists.views.artist_search', name='artist_search'),
    url(r'^search/event/', 'events.views.event_search', name='event_search'),
    url(r'^search/instrument/', 'artists.views.instrument_search', name='instrument_search'),
    url(r'^store/', include(application.urls)),
    url(r'^$', 'events.views.homepage', name="home"),
)

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^mission-statement/$', 'flatpage', {'url': '/mission-statement/'}, name='mission-statement'),
    url(r'^about-us/$', 'flatpage', {'url': '/about-us/'}, name='about-us'),
    url(r'^contact-and-info/$', 'flatpage', {'url': '/contact-and-info/'}, name='contact-and-info'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
