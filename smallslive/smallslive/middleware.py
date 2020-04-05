from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect


class RedirectMiddleware(object):
    """
    Redirect to maintenance screen
    """
    def process_request(self, request):
        host = request.get_host()
        if settings.REDIRECT_TO_MAINTENANCE and 'smallslive.com' in host:
            if 'maintenance' not in request.path:
                return HttpResponsePermanentRedirect(reverse('maintenance_view'))
