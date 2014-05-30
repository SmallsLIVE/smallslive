from django.core.urlresolvers import reverse_lazy
from allauth.account.views import LoginView as AllauthLoginView


class LoginView(AllauthLoginView):
    success_url = reverse_lazy('static_page', kwargs={'template_name': 'dashboard-musician'})

login_view = LoginView.as_view()