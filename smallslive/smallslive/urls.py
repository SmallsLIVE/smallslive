import os
from django.conf import settings
from django.apps import apps
from django.conf.urls.static import static
from django.conf.urls import  include, url
from django.urls import path, re_path, include
from django.contrib import admin
from django.urls import reverse_lazy
from django.http import Http404
from django.shortcuts import render_to_response
from django.views.generic.base import TemplateView, RedirectView
from django.template import TemplateDoesNotExist
#from paypal.express.dashboard.app import application as paypal_application
#from oscar.app import application
from django.contrib.sitemaps import views as sitemaps_views
from django.views.decorators.cache import cache_page
from oscar_apps.catalogue.views import ArtistCatalogue, get_album_catalog
from utils.views import OldSiteRedirectView
from .sitemaps import sitemaps
from newsletters.views import *
from artists.views import *
from events.views import *
from django.contrib.flatpages.views import flatpage

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


urlpatterns = [
    path(r'^dashboard/', include('artist_dashboard.urls')),
    url(r'^artist-registration/', include('artist_registration.urls')),
    url(r'^artists/', include('artists.urls')),
    url(r'^archive/(?P<year>\d+)/(?P<month>\d+)/$', RedirectView.as_view(permanent=True, pattern_name='search'),
        name='monthly_archive'),
    url(r'^archive/$', RedirectView.as_view(permanent=True, pattern_name='search'), name='archive'),
    url(r'^events/', include('events.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^static_page/(?P<template_name>[A-Za-z_-]*)/$', StaticPageView.as_view(), name="static_page"),
    path('admin/', admin.site.urls),
    path('', include(apps.get_app_config('oscar').urls[0])),
    # @TODO figure out this pages later
    # url(r'^about-us/$', static_pages.views.about_view, name="about-us"),
    # url(r'^photo-gallery/$', 'static_pages.views.gallery_view', name="photo-gallery"),
    # url(r'^press/$', 'static_pages.views.press_view', name="press"),

    url(r'^newsletters/$', newsletter_list, name="newsletters"),

    url(r'^accounts/', include('users.urls')),
    url(r'^subscriptions/', include('subscriptions.urls')),
    url(r'^multimedia/', include('multimedia.urls')),
    url(r'^institutional-subscriptions/', include('institutional_subscriptions.urls',
                                                  )),

    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^search/artist/', artist_search, name='artist_search'),
    url(r'^search/event/', event_search, name='event_search'),
    url(r'^search/instrument/', instrument_search, name='instrument_search'),
    url(r'^checkout/paypal/', include('paypal.express.urls')),
    #(r'^dashboard/paypal/express/', include(paypal_application.urls)), ## @TODO Fix later after upgrade
    url(r'^payments/', include('djstripe.urls', namespace="djstripe")),
    url(r'^catalog/accounts/login/$', RedirectView.as_view(url=reverse_lazy('accounts_login'))),
    #url(r'^catalog/', include(application.urls)),
    path('', include(apps.get_app_config('oscar').urls[0])),
    url(r'^catalog/artist-catalogue/', ArtistCatalogue.as_view(), name='artist_store'),
    url(r'^catalog/album-list/', get_album_catalog , name='album_list'),
    url(r'^sitemap\.xml$', cache_page(86400)(sitemaps_views.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(r'^sitemap-(?P<section>.+)\.xml$', cache_page(86400)(sitemaps_views.sitemap),
        {'sitemaps': sitemaps}, name='sitemaps'),
    url(r'^robots\.txt', static_file_view, kwargs={'file_name': 'robots.txt'}),
    url(r'^crossdomain\.xml', static_file_view, kwargs={'file_name': 'crossdomain.xml'}),
    url(r'^home/$', homepage, name="home"),
    url(r'^old/$', old_home, name="old_home"),
    url(r'^styles/$', styleguide, name="styles"),
    url(r'^donate/$', RedirectView.as_view(url=reverse_lazy('donate'), permanent=True)),
]

urlpatterns += [
    url(r'^terms-and-conditions/$', flatpage, {'url': '/terms-and-conditions/'}, name='terms-and-conditions'),
    url(r'^revenue-share/$', flatpage, {'url': '/revenue-share/'}, name='revenue-share'),
    url(r'^institutions/$', flatpage, {'url': '/institutions/'}, name='institutions'),
    url(r'^mezzrow/$', flatpage, {'url': '/mezzrow/'}, name='mezzrow'),
    url(r'^contact-and-info/$', flatpage, {'url': '/contact-and-info/'}, name='contact-and-info'),
    url(r'^education/$', flatpage, {'url': '/education/'}, name='education'),
    url(r'^venues-and-location/$', flatpage, {'url': '/venues-location/'}, name='venues-location'),
]

urlpatterns += [
    url(r'^join\.cfm$', RedirectView.as_view(url=reverse_lazy('signup_landing'), permanent=True)),
    url(r'^joinaudio\.cfm$', RedirectView.as_view(url=reverse_lazy('signup_landing'), permanent=True)),
    url(r'^musiccatalog\.cfm$', RedirectView.as_view(url=reverse_lazy('promotions:home'), permanent=True)),
    url(r'^indexnew\.cfm$', OldSiteRedirectView.as_view()),
    url(r'^innerclearback\.cfm$', OldSiteRedirectView.as_view()),
    url(r'^.*\.cfm$', OldSiteRedirectView.as_view()),
]

if settings.ENABLE_HIJACK:
    urlpatterns += url(r'^hijack/', include('hijack.urls')),

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
