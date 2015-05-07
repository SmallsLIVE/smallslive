from allauth.account import app_settings
from allauth.account.forms import ChangePasswordForm
from allauth.account.utils import complete_signup
from allauth.account.views import SignupView as AllauthSignupView, ConfirmEmailView as CoreConfirmEmailView,\
    LoginView as CoreLoginView
import braces.views
from braces.views import FormValidMessageMixin, LoginRequiredMixin
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from djstripe.mixins import SubscriptionMixin
from djstripe.models import Customer
from djstripe.settings import subscriber_request_callback
from djstripe.views import SyncHistoryView, ChangeCardView, ChangePlanView
from allauth.account.app_settings import EmailVerificationMethod
import stripe
from .forms import UserSignupForm, ChangeEmailForm, EditProfileForm, PlanForm


class SignupLandingView(TemplateView):
    template_name = 'account/signup-landing.html'

signup_landing = SignupLandingView.as_view()


class SignupView(AllauthSignupView):
    form_class = UserSignupForm

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        plan_name = self.kwargs.get('plan_name')
        plan = settings.SUBSCRIPTION_PLANS.get(plan_name)
        if not plan:
            raise Http404
        context['plan'] = plan
        self.request.session['selected_plan'] = plan_name
        if plan_name == "free":
            context['facebook_next_url'] = reverse('accounts_signup_complete')
        else:
            context['facebook_next_url'] = reverse('accounts_signup_payment', kwargs={'plan_name': plan_name})
        return context

    def form_valid(self, form):
        user = form.save(self.request)
        # if self.kwargs['plan_name'] == 'free':
        #     verification_method = EmailVerificationMethod.MANDATORY
        # else:
        #     verification_method = EmailVerificationMethod.OPTIONAL
        verification_method = EmailVerificationMethod.OPTIONAL
        complete_signup(self.request, user,
                        verification_method,
                        self.get_success_url())
        plan_name = self.kwargs.get('plan_name')
        self.selected_plan = plan_name
        return redirect(self.get_success_url())

    def get_success_url(self):
        if self.kwargs['plan_name'] == 'free':
            return reverse('accounts_signup_complete')
        else:
            return reverse('accounts_signup_payment', kwargs={'plan_name': self.kwargs['plan_name']})

signup_view = SignupView.as_view()


class SignupPaymentView(LoginRequiredMixin, FormValidMessageMixin, SubscriptionMixin, FormView):
    # TODO - needs tests

    form_class = PlanForm
    template_name = 'account/signup-payment.html'
    success_url = reverse_lazy("accounts_signup_complete")
    form_valid_message = "You are now subscribed!"

    def get_form_kwargs(self):
        kwargs = super(SignupPaymentView, self).get_form_kwargs()
        kwargs['selected_plan_type'] = self.kwargs.get('plan_name')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        plan_name = self.kwargs.get('plan_name')
        plan = settings.SUBSCRIPTION_PLANS.get(plan_name)
        if not plan:
            raise Http404
        context['plan'] = plan
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            try:
                customer, created = Customer.get_or_create(
                    subscriber=subscriber_request_callback(self.request))
                customer.update_card(self.request.POST.get("stripe_token"))
                customer.subscribe(form.cleaned_data["plan"])
            except stripe.StripeError as e:
                # add form error here
                self.error = e.args[0]
                return self.form_invalid(form)

            # redirect to confirmation page
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

signup_payment = SignupPaymentView.as_view()


class SignupCompleteView(LoginRequiredMixin, TemplateView):
    template_name = 'account/signup-complete.html'

    def get_context_data(self, **kwargs):
        context = super(SignupCompleteView, self).get_context_data(**kwargs)
        context['active_plan'] = self.request.user.get_subscription_plan
        return context

signup_complete = SignupCompleteView.as_view()


class SyncPaymentHistoryView(LoginRequiredMixin, SyncHistoryView):
    template_name = 'account/blocks/payment_history.html'

sync_payment_history = SyncPaymentHistoryView.as_view()


class SubscriptionSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'account/subscription-settings.html'

    def get_context_data(self, **kwargs):
        context = super(SubscriptionSettingsView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        return context

subscription_settings = SubscriptionSettingsView.as_view()


class UpdateCardView(ChangeCardView):
    def get_post_success_url(self):
        return reverse('subscription_settings')

    def get(self, request, *args, **kwargs):
        # only POST
        return redirect(self.get_post_success_url())

update_card = UpdateCardView.as_view()


class UpgradePlanView(ChangePlanView):
    form_class = PlanForm
    success_url = reverse_lazy("subscription_settings")
    template_name = 'account/upgrade_plan.html'

    def get_form_kwargs(self):
        kwargs = super(UpgradePlanView, self).get_form_kwargs()
        kwargs['selected_plan_type'] = self.kwargs.get('plan_name')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UpgradePlanView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        plan_name = self.kwargs.get('plan_name')
        plan = settings.SUBSCRIPTION_PLANS.get(plan_name)
        if not plan:
            raise Http404
        context['plan'] = plan
        context['stripe_token'] = self.request.user.customer.card_fingerprint
        return context

upgrade_plan = UpgradePlanView.as_view()


def user_settings_view(request):
    # if this is a POST request we need to process the form data
    if 'edit_profile' in request.POST:
        # create a form instance and populate it with data from the request:
        edit_profile_form = EditProfileForm(data=request.POST, user=request.user)
        # check whether it's valid:
        if edit_profile_form.is_valid():
            edit_profile_form.save(request)
            messages.success(request, "You've successfully updated your profile.")
            return HttpResponseRedirect('/')
    # if a GET (or any other method) we'll create a blank form
    else:
        edit_profile_form = EditProfileForm(user=request.user)

    if 'change_email' in request.POST:
        change_email_form = ChangeEmailForm(data=request.POST, user=request.user)
        if change_email_form.is_valid():
            change_email_form.save(request)
            messages.success(request, 'Your email address has been changed successfully.')
            return HttpResponseRedirect(reverse('account_email_verification_sent'))
    else:
        change_email_form = ChangeEmailForm(user=request.user)

    if 'change_password' in request.POST:
        change_password_form = ChangePasswordForm(data=request.POST, user=request.user)
        if change_password_form.is_valid():
            change_password_form.save()
            messages.success(request, 'Your password has been changed successfully.')
            return HttpResponseRedirect('/')
    else:
        change_password_form = ChangePasswordForm(user=request.user)

    return render(request, 'account/user_settings.html', {
        'change_email_form': change_email_form,
        'change_profile_form': edit_profile_form,
        'change_password_form': change_password_form,
    })


class ConfirmEmailView(CoreConfirmEmailView):
    def login_on_confirm(self, confirmation):
        """
        Redirects the user to the user settings page only after successfully confirming the email address.
        """
        resp = super(ConfirmEmailView, self).login_on_confirm(confirmation)
        if resp:
            if app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL:
                return HttpResponseRedirect(app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL)
            else:
                return HttpResponseRedirect('/')

confirm_email = ConfirmEmailView.as_view()


class LoginView(CoreLoginView):
    def get_template_names(self):
        if self.request.is_ajax():
            return ["account/ajax_login.html"]
        else:
            return ["account/login.html"]

login_view = LoginView.as_view()


class HasArtistAssignedMixin(braces.views.UserPassesTestMixin):
    def test_func(self, user):
        self.logged_in = user.is_authenticated()
        if not self.logged_in:
            return False
        self.has_artist = user.artist_id is not None
        return self.has_artist

    def get_login_url(self):
        if not self.logged_in:
            return reverse('artist_dashboard:login')
        else:
            messages.error(self.request, 'You need to be an artist to access that part of the site.')
            return reverse('home')
