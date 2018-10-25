from allauth.account import app_settings
from datetime import datetime, date
from allauth.account.forms import ChangePasswordForm
from allauth.account.models import EmailAddress
from allauth.account.utils import complete_signup
from allauth.account.views import SignupView as AllauthSignupView, \
    ConfirmEmailView as CoreConfirmEmailView, \
    LoginView as CoreLoginView, _ajax_response
import braces.views
from braces.views import FormValidMessageMixin, LoginRequiredMixin, StaffuserRequiredMixin
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, ListView
from djstripe.mixins import SubscriptionMixin
from djstripe.models import Customer, Charge, Plan
from djstripe.settings import subscriber_request_callback
from djstripe.views import SyncHistoryView, ChangeCardView, ChangePlanView,\
    CancelSubscriptionView as BaseCancelSubscriptionView
from allauth.account.app_settings import EmailVerificationMethod
from urllib import urlencode
import urlparse
import stripe

from artist_dashboard.forms import ArtistInfoForm
from custom_stripe.models import CustomPlan, CustomerDetail
from users.models import SmallsUser
from users.utils import charge, subscribe_to_plan, one_time_donation
from .forms import UserSignupForm, ChangeEmailForm, EditProfileForm, PlanForm, ReactivateSubscriptionForm
from wkhtmltopdf.views import PDFTemplateView


# TODO: remove duplicate code (views and templates)
class DonateView(TemplateView):

    
    def get_template_names(self):
        if self.request.is_ajax():
            template_name = 'account/donate.html'
        else:
           template_name = 'account/donate-event.html'
        return [template_name]
        

    def get_context_data(self, **kwargs):
        context = super(DonateView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        context['form_action'] = reverse('donate')
        context['redirect_url'] = self.request.META.get('HTTP_REFERER')
       
        return context
        

    def post(self, request, *args, **kwargs):

        stripe_token = self.request.POST.get('stripe_token')
        amount = int(self.request.POST.get('quantity'))
        redirect_url = self.request.POST.get('redirect_url')

        try:
            customer, created = Customer.get_or_create(
                subscriber=subscriber_request_callback(request))
            one_time_donation(customer, stripe_token, amount)
        except stripe.StripeError as e:
            print 'Except -->'
            print e
            # add form error here
            return _ajax_response(request, JsonResponse({
                'error': e.args[0]
            }, status=500))

        return _ajax_response(
            request, redirect(reverse(
                'donate_complete') + '?redirect_url={}'.format(redirect_url))
        )


donate = DonateView.as_view()


class DonateCompleteView(DonateView):

    def get_context_data(self, **kwargs):
        context = super(
            DonateCompleteView, self
        ).get_context_data(**kwargs)
        context['completed'] = True
        context['redirect_url'] = self.request.GET.get('redirect_url')

        print 'DonateCompleteView: get_context_data'
        print context
        print '----------------------------------------------'

        return context


donate_complete = DonateCompleteView.as_view()


class BecomeSupporterView(TemplateView):
    template_name = 'account/become-supporter.html'

    def get_context_data(self, **kwargs):
        context = super(BecomeSupporterView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        context['form_action'] = reverse('become_supporter')
        return context

    def post(self, request, *args, **kwargs):

        stripe_token = self.request.POST.get('stripe_token')
        plan_type = self.request.POST.get('type')
        amount = int(self.request.POST.get('quantity'))

        # As per Aslan's request
        # Yearly donations will no longer exist. They are One Time Donations  now.

        try:
            customer, created = Customer.get_or_create(
                subscriber=subscriber_request_callback(request))
            if plan_type == 'month':
                subscribe_to_plan(customer, stripe_token, amount, plan_type)
            else:
                grant = amount >= 100
                one_time_donation(customer, stripe_token, amount,
                                  grant_access_to_archive=grant)
        except stripe.StripeError as e:
            # add form error here
            return _ajax_response(request, JsonResponse({
                'error': e.args[0]
            }, status=500))

        return _ajax_response(
            request, redirect(reverse('become_supporter_complete'))
        )


become_supporter = BecomeSupporterView.as_view()


class BecomeSupporterCompleteView(BecomeSupporterView):
    def get_context_data(self, **kwargs):
        context = super(
            BecomeSupporterCompleteView, self
        ).get_context_data(**kwargs)
        context['completed'] = True

        print 'BecomeSupporterCompleteView: get_context_data'
        print context
        print '----------------------------------------------'

        return context


become_supporter_complete = BecomeSupporterCompleteView.as_view()


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

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def form_valid(self, form):
        user = form.save(self.request)
        # if self.kwargs['plan_name'] == 'free':
        #     verification_method = EmailVerificationMethod.MANDATORY
        # else:
        #     verification_method = EmailVerificationMethod.OPTIONAL
        verification_method = EmailVerificationMethod.OPTIONAL
        complete_signup(
            self.request, user, verification_method, self.get_success_url()
        )

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('home')


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


class SyncPaymentHistoryView(SyncHistoryView):
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




@login_required
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
        'current_user' : request.user,
    })

@login_required
def user_settings_view_new(request):

    # if this is a POST request we need to process the form data
    if 'edit_profile' in request.POST:
        # create a form instance and populate it with data from the request:
        edit_profile_form = EditProfileForm(data=request.POST, user=request.user)
        # check whether it's valid:
        if edit_profile_form.is_valid():
            edit_profile_form.save(request)
            messages.success(request, "You've successfully updated your profile.")
            return HttpResponseRedirect('/accounts/settings/')
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
            return HttpResponseRedirect('/accounts/settings/')
    else:
        change_password_form = ChangePasswordForm(user=request.user)
    
    # if this is a POST request we need to process the form data
    if 'artist_info' in request.POST:
        # create a form instance and populate it with data from the request:
        artist_info_form = ArtistInfoForm(data=request.POST, instance=request.user)
        # check whether it's valid:
        if artist_info_form.is_valid():
            artist_info_form.save(request)
            messages.success(request, "You've successfully updated your profile.")
            return HttpResponseRedirect('/accounts/settings/')
    # if a GET (or any other method) we'll create a blank form
    else:
        artist_info_form = ArtistInfoForm(instance=request.user)
    #Context for strip info

    plan = None
    period_end = {}
    period_end["date"] = None
    monthly_pledge_in_dollars = None
    customer = request.user.customer
    user_archive_access_until = request.user.archive_access_until

    if customer.has_active_subscription():
        plan_id = request.user.customer.current_subscription.plan
        plan = stripe.Plan.retrieve(id=plan_id)

    customer_charges = customer.charges.all()
   
    charges_value =0
    for charge in customer_charges:
        charges_value += charge.amount
 
        artist_info_form = ArtistInfoForm(instance=request.user)
    customer_detail = CustomerDetail.get(id=request.user.customer.stripe_id)
    if customer_detail.subscription:
        monthly_pledge_in_dollars = customer_detail.subscription.plan.amount/100
    print(customer_detail)
    print(dir(customer_detail))

    if customer_detail.subscription:
        period_end["date"] = datetime.fromtimestamp(customer_detail.subscription.current_period_end).strftime("%d/%m/%y")
        period_end["due"] = datetime.fromtimestamp(customer_detail.subscription.current_period_end) <= datetime.now()

    if customer_detail.subscriptions.data:
        cancel_at = customer_detail.subscriptions.data[0]['cancel_at_period_end']
    else:
        cancel_at = False
    return render(request, 'account/user_settings_new.html', {
        'change_email_form': change_email_form,
        'change_profile_form': edit_profile_form,
        'change_password_form': change_password_form,
        'current_user': request.user,
        'artist_info_form': artist_info_form,
        'plan': plan,
        'customer_charges': customer_charges,
        'customer_detail': customer_detail,
        'charges_value': charges_value,
        'period_end': period_end,
        'user_archive_access_until': user_archive_access_until,
        'monthly_pledge_in_dollars': monthly_pledge_in_dollars,
        'cancelled': cancel_at,
        'donate_url': reverse('donate')
    })



class UserTaxLetter(PDFTemplateView):

    filename = 'tax_letter.pdf'
    template_name = 'account/tax-letter.html'
    
    
    def get_context_data(self, **kwargs):
        context = super(UserTaxLetter, self).get_context_data(**kwargs)
        customer =  self.request.user.customer
        customer_charges = customer.charges.all()
        charges_value = 0
        for charge in customer_charges:
            charges_value += charge.amount
        context['customer'] = customer
        context['charges_value'] = charges_value
        context['year'] = 1964
        return context

user_tax_letter = UserTaxLetter.as_view()


class ConfirmEmailView(CoreConfirmEmailView):

    def get_redirect_url(self):
        # Add offer parameter to url, or `next` if it's login.
        url = super(ConfirmEmailView, self).get_redirect_url()
        if 'login' in url:
            parts = list(urlparse.urlparse(url))
            query = urlparse.parse_qs(parts[4])
            query['next'] = '{}?offer=subscribe'.format(
                settings.LOGIN_REDIRECT_URL
            )
            parts[4] = urlencode(query)
            url = urlparse.urlunparse(parts)
        else:
            parts = list(urlparse.urlparse(url))
            query = urlparse.parse_qs(parts[4])
            query.update({'offer': 'subscribe'})
            parts[4] = urlencode(query)
            url = urlparse.urlunparse(parts)
        return url

confirm_email = ConfirmEmailView.as_view()


class LoginView(CoreLoginView):
    def get_template_names(self):
        if self.request.is_ajax():
            return ["account/ajax_login.html"]
        else:
            return ["account/login.html"]

login_view = LoginView.as_view()


class CancelSubscriptionView(BaseCancelSubscriptionView):
    success_url = reverse_lazy("user_settings_new")

cancel_subscription = CancelSubscriptionView.as_view()


class ReactivateSubscriptionView(FormView):
    success_url = reverse_lazy("subscription_settings")
    form_class = ReactivateSubscriptionForm

    def form_valid(self, form):
        customer, created = Customer.get_or_create(
            subscriber=subscriber_request_callback(self.request))

        if customer.has_active_subscription() and customer.current_subscription.cancel_at_period_end:
            customer.subscribe(customer.current_subscription.plan)

            messages.info(self.request, "You have reactivated your subscription. It expires at '{period_end}'.".format(
                period_end=customer.current_subscription.current_period_end))

        return super(ReactivateSubscriptionView, self).form_valid(form)

reactivate_subscription = ReactivateSubscriptionView.as_view()


class SubscriberEmailsFilterView(StaffuserRequiredMixin, ListView):
    content_type = 'text/plain'
    paginate_by = 3000
    template_name = "account/subscriber_list_emails.html"
    context_object_name = 'subscribers'

    def get_queryset(self):
        return SmallsUser.objects.filter(artist=None).values_list('email', flat=True).nocache()

subscriber_list_emails = SubscriberEmailsFilterView.as_view()


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


class HasArtistAssignedOrIsSuperuserMixin(HasArtistAssignedMixin):
    def test_func(self, user):
        self.logged_in = user.is_authenticated()
        if not self.logged_in:
            return False
        self.has_artist = user.artist_id is not None
        return self.has_artist or user.is_superuser


class ResendEmailConfirmationView(StaffuserRequiredMixin, ListView):
    template_name = 'account/admin_email.html'
    queryset = EmailAddress.objects.order_by('email')

    def get_context_data(self, **kwargs):
        context = super(ResendEmailConfirmationView, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        context = { 'object_list' : {}, }
        # if form.is_valid():
        #     return self.form_valid(form)
        # else:
        #     return self.form_invalid(form)
        return context



admin_email_confirmation = ResendEmailConfirmationView.as_view()

