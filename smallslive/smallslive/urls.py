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
from django.contrib.sitemaps.views import sitemap
from .sitemaps import sitemaps


# uncomment these lines to enable the Djrill admin interface 
#from djrill import DjrillAdminSite
#admin.site = DjrillAdminSite()

admin.autodiscover()


class StaticPageView(TemplateView):
    def get_template_names(self):
        template_name = os.path.join(settings.BASE_DIR, 'templates', "{0}.html".format(self.kwargs['template_name']))
        if not os.path.exists(template_name):
            raise Http404
        return [template_name]


def robots_view(request):
    return render_to_response("robots.txt", content_type="text/plain")


urlpatterns = patterns('',
    url(r'^dashboard/', include('artist_dashboard.urls', app_name="artist_dashboard", namespace="artist_dashboard")),
    url(r'^artist-registration/', include('artist_registration.urls', app_name="artist_registration")),
    url(r'^artists/', include('artists.urls', app_name="artists")),
    url(r'^events/', include('events.urls', app_name="events")),
    url(r'^search/', include('search.urls', app_name="search")),
    url(r'^static_page/(?P<template_name>[A-Za-z_-]*)/$', StaticPageView.as_view(), name="static_page"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about-us/$', 'static_pages.views.about_view', name="about-us"),
    url(r'^photo-gallery/$', 'static_pages.views.gallery_view', name="photo-gallery"),
    url(r'^press/$', 'static_pages.views.press_view', name="press"),
    url(r'^newsletters/$', 'newsletters.views.newsletter_list', name="newsletters"),

    url(r'^accounts/', include('users.urls')),
    url(r'^multimedia/', include('multimedia.urls')),

    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^search/artist/', 'artists.views.artist_search', name='artist_search'),
    url(r'^search/event/', 'events.views.event_search', name='event_search'),
    url(r'^search/instrument/', 'artists.views.instrument_search', name='instrument_search'),
    (r'^checkout/paypal/', include('paypal.express.urls')),
    (r'^dashboard/paypal/express/', include(paypal_application.urls)),
    url(r'^payments/', include('djstripe.urls', namespace="djstripe")),
    url(r'^store/accounts/login/$', RedirectView.as_view(url=reverse_lazy('accounts_login'))),
    url(r'^store/', include(application.urls)),
    url(r'^robots\.txt', robots_view),
    url(r'^sitemap.xml', include('static_sitemaps.urls')),
    #url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^$', 'events.views.homepage', name="home"),
)


urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^terms-and-conditions/$', 'flatpage', {'url': '/terms-and-conditions/'}, name='terms-and-conditions'),
    url(r'^revenue-share/$', 'flatpage', {'url': '/revenue-share/'}, name='revenue-share'),
    url(r'^benefactors/$', 'flatpage', {'url': '/benefactors/'}, name='benefactors'),
    url(r'^contact-and-info/$', 'flatpage', {'url': '/contact-and-info/'}, name='contact-and-info'),
)


# URL redirects from old site
class OldSiteRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if self.request.GET.get('itemCategory') == '43178':
            return reverse_lazy('contact-and-info')
        elif self.request.GET.get('itemCategory') == '43179':
            return reverse_lazy('live-stream')
        elif self.request.GET.get('itemCategory') == '32321':
            return reverse_lazy('live-stream')
        return reverse_lazy('home')


urlpatterns += patterns('',
    url(r'^join\.cfm$', RedirectView.as_view(url=reverse_lazy('signup_landing'), permanent=True)),
    url(r'^joinaudio\.cfm$', RedirectView.as_view(url=reverse_lazy('signup_landing'), permanent=True)),
    url(r'^musiccatalog\.cfm$', RedirectView.as_view(url=reverse_lazy('promotions:home'), permanent=True)),
    url(r'^indexnew\.cfm$', OldSiteRedirectView.as_view()),
    url(r'^innerclearback\.cfm$', OldSiteRedirectView.as_view()),
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
