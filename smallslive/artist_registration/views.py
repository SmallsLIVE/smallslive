from allauth.account import views as allauth_views
from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import perform_login
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import Http404
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic.edit import FormView
from artists.models import Artist
from .forms import CompleteSignupForm, InviteArtistForm


class InviteArtistView(FormView):
    form_class = InviteArtistForm
    template_name = "artist_registration/invite_artist.html"

    def get_context_data(self, **kwargs):
        context = super(InviteArtistView, self).get_context_data(**kwargs)
        context['artist'] = self.artist
        return context

    def get_form_kwargs(self):
        kwargs = super(InviteArtistView, self).get_form_kwargs()
        self.artist = Artist.objects.get(pk=self.kwargs.get('artist'))
        kwargs['artist'] = self.artist
        return kwargs

    def form_valid(self, form):
        response = super(InviteArtistView, self).form_valid(form)
        form.invite_artist(self.request)
        return response

    def get_success_url(self):
        return reverse('artist_edit', kwargs={'pk': self.artist.id, 'slug': self.artist.slug})


class ConfirmEmailView(allauth_views.ConfirmEmailView):
    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            return self.post(*args, **kwargs)
        except Http404:
            self.object = None
        ctx = self.get_context_data()
        return self.render_to_response(ctx)

    def post(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        get_adapter().add_message(self.request,
                                  messages.SUCCESS,
                                  'account/messages/email_confirmed.txt',
                                  {'email': confirmation.email_address.email})
        resp = self.login_on_confirm(confirmation)
        if resp:
            return resp
        # Don't -- allauth doesn't touch is_active so that sys admin can
        # use it to block users et al
        #
        # user = confirmation.email_address.user
        # user.is_active = True
        # user.save()
        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)
        return redirect(redirect_url)

    def get_redirect_url(self):
        return reverse('artist_registration_password_set')

    def login_on_confirm(self, confirmation):
        """
        Automatically log in the artist when he clicks the activation link and
        delete the confirmation model to prevent further login with that confirmation
        link in order to improve security.
        """
        date = timezone.now()
        user = confirmation.email_address.user
        user.is_active = True
        user.date_joined = date
        user.last_login = date
        user.save()
        confirmation.delete()
        if self.request.user.is_anonymous():
            return perform_login(self.request,
                                 user,
                                 app_settings.EmailVerificationMethod.NONE,
                                 redirect_url=self.get_redirect_url())

confirm_email = ConfirmEmailView.as_view()


class PasswordSetView(allauth_views.PasswordSetView):
    form_class = CompleteSignupForm
    success_url = reverse_lazy('artist_dashboard:home')
    template_name = 'artist_registration/set_password.html'

password_set = PasswordSetView.as_view()
