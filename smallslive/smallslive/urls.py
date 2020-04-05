import os
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import render_to_response
from django.views.generic.base import TemplateView, RedirectView
from django.template import TemplateDoesNotExist
from paypal.express.dashboard.app import application as paypal_application
from oscar.app import application
from django.contrib.sitemaps import views as sitemaps_views
from django.views.decorators.cache import cache_page
from oscar_apps.catalogue.views import ArtistCatalogue, get_album_catalog
from utils.views import OldSiteRedirectView
from .sitemaps import sitemaps

# uncomment these lines to enable the Djrill admin interface 
# from djrill import DjrillAdminSite
# admin.site = DjrillAdminSite()

admin.autodiscover()


class StaticPageView(TemplateView):

    def get_template_names(self):
        template_name = os.path.join(settings.BASE_DIR, 'templates', "{0}.html".format(self.kwargs['template_name']))
        if not os.path.exists(template_name):
            raise Http404
        return [template_name]


def static_file_view(request, **kwargs):
    file_name = kwargs.get("file_name")
    if file_name.endswith('xml'):
        content_type = 'application/xml'
    else:
        content_type = 'text/plain'
    response = render_to_response(file_name, content_type=content_type)
    response['Access-Control-Allow-Origin'] = '*'
    response['Cache-Control'] = 'public, max-age=3600'
    return response


urlpatterns = patterns('',
    url(r'^dashboard/', include('artist_dashboard.urls', app_name="artist_dashboard", namespace="artist_dashboard")),
    url(r'^artist-registration/', include('artist_registration.urls', app_name="artist_registration")),
    url(r'^artists/', include('artists.urls', app_name="artists")),
    url(r'^archive/(?P<year>\d+)/(?P<month>\d+)/$', RedirectView.as_view(permanent=True, pattern_name='search'),
        name='monthly_archive'),
    url(r'^archive/$', RedirectView.as_view(permanent=True, pattern_name='search'), name='archive'),
    url(r'^events/', include('events.urls', app_name="events")),
    url(r'^search/', include('search.urls', app_name="search")),
    url(r'^static_page/(?P<template_name>[A-Za-z_-]*)/$', StaticPageView.as_view(), name="static_page"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about-us/$', 'static_pages.views.about_view', name="about-us"),
    url(r'^photo-gallery/$', 'static_pages.views.gallery_view', name="photo-gallery"),
    url(r'^press/$', 'static_pages.views.press_view', name="press"),
    url(r'^newsletters/$', 'newsletters.views.newsletter_list', name="newsletters"),

    url(r'^accounts/', include('users.urls')),
    url(r'^subscriptions/', include('subscriptions.urls')),
    url(r'^multimedia/', include('multimedia.urls')),
    url(r'^institutional-subscriptions/', include('institutional_subscriptions.urls',
                                                  app_name="institutional_subscriptions")),

    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^search/artist/', 'artists.views.artist_search', name='artist_search'),
    url(r'^search/event/', 'events.views.event_search', name='event_search'),
    url(r'^search/instrument/', 'artists.views.instrument_search', name='instrument_search'),
    (r'^checkout/paypal/', include('paypal.express.urls')),
    (r'^dashboard/paypal/express/', include(paypal_application.urls)),
    url(r'^payments/', include('djstripe.urls', namespace="djstripe")),
    url(r'^catalog/accounts/login/$', RedirectView.as_view(url=reverse_lazy('accounts_login'))),
    url(r'^catalog/', include(application.urls)),
    url(r'^catalog/artist-catalogue/', ArtistCatalogue.as_view(), name='artist_store'),
    url(r'^catalog/album-list/', get_album_catalog , name='album_list'),
    url(r'^sitemap\.xml$', cache_page(86400)(sitemaps_views.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(r'^sitemap-(?P<section>.+)\.xml$', cache_page(86400)(sitemaps_views.sitemap),
        {'sitemaps': sitemaps}, name='sitemaps'),
    url(r'^robots\.txt', static_file_view, kwargs={'file_name': 'robots.txt'}),
    url(r'^crossdomain\.xml', static_file_view, kwargs={'file_name': 'crossdomain.xml'}),
    url(r'^$', 'events.views.homepage', name="home"),
    url(r'^old/$', 'events.views.old_home', name="old_home"),
    url(r'^styles/$', 'events.views.styleguide', name="styles"),
    url(r'^donate/$', RedirectView.as_view(url=reverse_lazy('donate'), permanent=True)),
)

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^terms-and-conditions/$', 'flatpage', {'url': '/terms-and-conditions/'}, name='terms-and-conditions'),
    url(r'^revenue-share/$', 'flatpage', {'url': '/revenue-share/'}, name='revenue-share'),
    url(r'^institutions/$', 'flatpage', {'url': '/institutions/'}, name='institutions'),
    url(r'^mezzrow/$', 'flatpage', {'url': '/mezzrow/'}, name='mezzrow'),
    url(r'^contact-and-info/$', 'flatpage', {'url': '/contact-and-info/'}, name='contact-and-info'),
    url(r'^education/$', 'flatpage', {'url': '/education/'}, name='education'),
    url(r'^venues-and-location/$', 'flatpage', {'url': '/venues-location/'}, name='venues-location'),
)

urlpatterns += patterns('',
    url(r'^join\.cfm$', RedirectView.as_view(url=reverse_lazy('signup_landing'), permanent=True)),
    url(r'^joinaudio\.cfm$', RedirectView.as_view(url=reverse_lazy('signup_landing'), permanent=True)),
    url(r'^musiccatalog\.cfm$', RedirectView.as_view(url=reverse_lazy('promotions:home'), permanent=True)),
    url(r'^indexnew\.cfm$', OldSiteRedirectView.as_view()),
    url(r'^innerclearback\.cfm$', OldSiteRedirectView.as_view()),
    url(r'^.*\.cfm$', OldSiteRedirectView.as_view()),
)

if settings.ENABLE_HIJACK:
    urlpatterns += url(r'^hijack/', include('hijack.urls')),

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
