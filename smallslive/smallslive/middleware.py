from django.shortcuts import redirect
from django.contrib.auth import logout
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect


class RedirectMiddleware(object):
    """
    Redirect to maintenance screen
    """
    def process_request(self, request):
        host = request.get_host()
        if settings.REDIRECT_TO_MAINTENANCE and 'smallslive.com' in host:
            if 'maintenance' not in request.path:
                return HttpResponseRedirect(reverse('maintenance_view'))


class DisableMemberLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.access_level == 'member':
                logout(request)
                return redirect('home')  # Redirect to an appropriate page

        response = self.get_response(request)
        return response