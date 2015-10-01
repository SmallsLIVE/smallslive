from allauth.account import views as allauth_views
from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailConfirmation
from allauth.account.utils import perform_login
from allauth.account.views import sensitive_post_parameters_m
from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import logout
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import Http404, HttpResponseRedirect
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


class ArtistAccountActivateView(allauth_views.PasswordSetView):
    form_class = CompleteSignupForm
    success_url = reverse_lazy('artist_dashboard:home')
    template_name = 'artist_registration/set_password.html'

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous() and request.user.has_usable_password():
            return HttpResponseRedirect(self.success_url)
        return super(allauth_views.PasswordSetView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(key=self.kwargs["key"].lower())
        except EmailConfirmation.DoesNotExist:
            raise Http404()
        
    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            return self.post(*args, **kwargs)
        except Http404:
            self.object = None
        return super(ArtistAccountActivateView, self).get(*args, **kwargs)

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs

    def get_form_kwargs(self):
        kwargs = super(allauth_views.PasswordSetView, self).get_form_kwargs()
        confirmation = self.get_object()
        kwargs["user"] = confirmation.email_address.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(ArtistAccountActivateView, self).get_context_data(**kwargs)
        ctx["confirmation"] = self.get_object()
        return ctx

    def form_valid(self, form):
        logout(self.request)
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        get_adapter().add_message(self.request,
                                  messages.SUCCESS,
                                  'account/messages/email_confirmed.txt',
                                  {'email': confirmation.email_address.email})
        form.save()
        resp = self.login_on_confirm(confirmation)
        if resp:
            return resp
        # Don't -- allauth doesn't touch is_active so that sys admin can
        # use it to block users et al
        #
        # user = confirmation.email_address.user
        # user.is_active = True
        # user.save()
        redirect_url = self.success_url
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)
        return redirect(redirect_url)

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
        if not self.request.user.is_anonymous():
            logout(self.request)
        return perform_login(self.request,
                             user,
                             app_settings.EmailVerificationMethod.NONE,
                             redirect_url=self.success_url)


artist_account_activate = ArtistAccountActivateView.as_view()
