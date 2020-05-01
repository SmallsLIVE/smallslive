from datetime import datetime, date
import json
import stripe
from wkhtmltopdf.views import PDFTemplateView
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, ListView, View
from django.utils import timezone
from allauth.account.app_settings import EmailVerificationMethod
from allauth.account.forms import ChangePasswordForm
from users.models import SmallsEmailAddress
from allauth.account.views import SignupView as AllauthSignupView, \
    LoginView as CoreLoginView, _ajax_response
import braces.views
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from djstripe.models import Customer, Charge, Plan
from djstripe.settings import subscriber_request_callback

from artist_dashboard.forms import ArtistInfoForm
from custom_stripe.models import CustomPlan, CustomerDetail
from users.utils import charge, \
    one_time_donation, subscribe_to_plan, update_active_card
from .forms import UserSignupForm, ChangeEmailForm, EditProfileForm
from oscar_apps.checkout.forms import BillingAddressForm
from oscar.apps.address.models import UserAddress
from .utils import complete_signup


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
            context['facebook_next_url'] = reverse(
                'accounts_signup_payment', kwargs={'plan_name': plan_name})

        return context

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def get_form_kwargs(self):

        kwargs = super(SignupView, self).get_form_kwargs()

        # We assume email addresses match if the user
        # hasn't submitted email address confirmation
        kwargs['ignore_email2'] = False
        if self.request.POST:
            if 'email2' not in self.request.POST:
                kwargs['ignore_email2'] = True

        return kwargs

    def form_valid(self, form, **kwargs):
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


signup_view = SignupView.as_view()


class SignupCompleteView(LoginRequiredMixin, TemplateView):
    template_name = 'account/signup-complete.html'

    def get_context_data(self, **kwargs):
        context = super(SignupCompleteView, self).get_context_data(**kwargs)
        context['active_plan'] = self.request.user.get_subscription_plan
        return context


signup_complete = SignupCompleteView.as_view()


@login_required
def user_settings_view(request):
    # if this is a POST request we need to process the form data
    if 'edit_profile' in request.POST:
        # create a form instance and populate it with data from the request:
        edit_profile_form = EditProfileForm(
            data=request.POST, user=request.user)
        # check whether it's valid:
        if edit_profile_form.is_valid():
            edit_profile_form.save(request)
            messages.success(
                request, "You've successfully updated your profile.")
            return HttpResponseRedirect('/')
    # if a GET (or any other method) we'll create a blank form
    else:
        edit_profile_form = EditProfileForm(user=request.user)

    if 'change_email' in request.POST:
        change_email_form = ChangeEmailForm(
            data=request.POST, user=request.user)
        if change_email_form.is_valid():
            change_email_form.save(request)
            messages.success(
                request, 'Your email address has been changed successfully.')
            return HttpResponseRedirect(reverse('account_email_verification_sent'))
    else:
        change_email_form = ChangeEmailForm(user=request.user)

    if 'change_password' in request.POST:
        change_password_form = ChangePasswordForm(
            data=request.POST, user=request.user)
        if change_password_form.is_valid():
            change_password_form.save()
            messages.success(
                request, 'Your password has been changed successfully.')
            return HttpResponseRedirect('/')
    else:
        change_password_form = ChangePasswordForm(user=request.user)

    return render(request, 'account/user_settings.html', {
        'change_email_form': change_email_form,
        'change_profile_form': edit_profile_form,
        'change_password_form': change_password_form,
        'current_user': request.user,
    })


@login_required(login_url='home')
def user_settings_view_new(request):
    profile_updated = False
    # if this is a POST request we need to process the form data
    if 'edit_profile' in request.POST:
        # create a form instance and populate it with data from the request:
        edit_profile_form = EditProfileForm(
            data=request.POST, user=request.user)
        # check whether it's valid:
        if edit_profile_form.is_valid():
            edit_profile_form.save(request)
            messages.success(
                request, "You've successfully updated your profile.")
            profile_updated = True
    # if a GET (or any other method) we'll create a blank form
    else:
        edit_profile_form = EditProfileForm(user=request.user)

    if 'edit_active_card' in request.POST:
        try:
            stripe_token = request.POST.get('stripe_token')
            customer, created = Customer.get_or_create(
                subscriber=subscriber_request_callback(request))
            update_active_card(customer, stripe_token)
        except stripe.StripeError as e:
            # add form error here
            return _ajax_response(request, JsonResponse({
                'error': e.args[0]
            }, status=500))

        messages.success(
            request, 'Your account card has been changed successfully.')
        profile_updated = True

    if 'change_email' in request.POST:
        change_email_form = ChangeEmailForm(
            data=request.POST, user=request.user)
        if change_email_form.is_valid():
            change_email_form.save(request)
            messages.success(
                request, 'Your email address has been changed successfully.')
            profile_updated = True
    else:
        change_email_form = ChangeEmailForm(user=request.user)

    if 'change_password' in request.POST:
        change_password_form = ChangePasswordForm(
            data=request.POST, user=request.user)
        if change_password_form.is_valid():
            change_password_form.save()
            messages.success(
                request, 'Your password has been changed successfully.')
            profile_updated = True
    else:
        change_password_form = ChangePasswordForm(user=request.user)

    # if this is a POST request we need to process the form data
    if 'artist_info' in request.POST:
        # create a form instance and populate it with data from the request:
        artist_info_form = ArtistInfoForm(
            data=request.POST, instance=request.user)
        # check whether it's valid:
        if artist_info_form.is_valid():
            artist_info_form.save(request)
            messages.success(
                request, "You've successfully updated your profile.")
            profile_updated = True
    # if a GET (or any other method) we'll create a blank form
    else:
        artist_info_form = ArtistInfoForm(instance=request.user)

    if 'billing_info' in request.POST:
        billing_address_form = BillingAddressForm(
            None, request.user, request.POST)
        if billing_address_form.is_valid():
            billing_address_form.save()
            profile_updated = True
        else:
            billing_address_form = BillingAddressForm(None, request.user, None)

    if profile_updated:
        return HttpResponseRedirect('/accounts/settings/')

    plan = None
    period_end = {}
    period_end['date'] = None

    customer_detail = None
    customer_charges = None
    user_archive_access_until = None
    monthly_pledge_in_dollars = None
    cancel_at = None
    billing_address = None

    show_email_confirmation = False

    if not request.user.has_activated_account:
        show_email_confirmation = True
    else:
        try:
            customer = request.user.customer
        except:
            customer = None

        user_archive_access_until = None
        if request.user.has_archive_access:
            user_archive_access_until = request.user.get_archive_access_expiry_date()

        if customer and customer.has_active_subscription():
            plan_id = request.user.customer.current_subscription.plan
            try:
                plan = stripe.Plan.retrieve(id=plan_id)
            except stripe.error.InvalidRequestError:
                plan = None

        customer_charges = request.user.get_donations().order_by('-date')
        charges_value = 0
        for charge in customer_charges:
            if charge.amount:
                charges_value = charges_value + charge.amount

            artist_info_form = ArtistInfoForm(instance=request.user)
        customer_detail = CustomerDetail.get(
            id=request.user.customer.stripe_id)
        if customer_detail and customer_detail.subscription:
            monthly_pledge_in_dollars = customer_detail.subscription.plan.amount / 100

        if customer_detail and customer_detail.subscription:
            period_end["date"] = datetime.fromtimestamp(
                customer_detail.subscription.current_period_end).strftime("%d/%m/%y")
            period_end["due"] = datetime.fromtimestamp(
                customer_detail.subscription.current_period_end) <= datetime.now()

        if customer_detail and customer_detail.subscription and customer_detail.subscriptions.data:
            cancel_at = customer_detail.subscriptions.data[0]['cancel_at_period_end']
        else:
            cancel_at = False

        try:
            billing_address = request.user.addresses.get(
                is_default_for_billing=True)
        except UserAddress.DoesNotExist:
            try:
                billing_address = request.user.addresses.first()
            except UserAddress.DoesNotExist:
                billing_address = UserAddress()

    return render(request, 'account/user_settings_new.html', {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'change_email_form': change_email_form,
        'change_profile_form': edit_profile_form,
        'change_password_form': change_password_form,
        'current_user': request.user,
        'artist_info_form': artist_info_form,
        'plan': plan,
        'donations': request.user.get_donations() or None,
        'customer_detail': customer_detail or '',
        'customer_charges': customer_charges or '',
        'charges_value': request.user.get_donation_amount or '0',
        'period_end': period_end,
        'user_archive_access_until': user_archive_access_until or 'unverified account',
        'monthly_pledge_in_dollars': monthly_pledge_in_dollars or 'no',
        'cancelled': cancel_at or '',
        'donate_url': reverse('donate'),
        'billing_address': billing_address or '',
        'show_email_confirmation_dialog': show_email_confirmation
    })


def check_account_status(request):
    user = request.user
    is_authenticated = user.is_authenticated()
    data = {
        'isAuthenticated': is_authenticated,
        'isVerified': is_authenticated and user.has_activated_account,
    }
    response = json.dumps({'success': True,
                           'data': data})

    return HttpResponse(response, content_type="application/json")


class UserTaxLetterHtml(TemplateView):

    template_name = 'account/tax-letter.html'

    def get_context_data(self, **kwargs):
        context = super(UserTaxLetterHtml, self).get_context_data(**kwargs)
        customer = self.request.user.customer
        customer_charges = customer.subscriber.get_donations()
        charges_value = 0
        deductable_value = 0
        for charge in customer_charges:
            charges_value += charge.amount
        for charge in customer_charges:
            deductable_value += charge.deductable_amount
        if deductable_value == 0 and charges_value > 0:
            deductable_value = charges_value
        context['customer'] = customer
        context['deductable_value'] = deductable_value
        context['charges_value'] = charges_value
        context['year'] = timezone.now().year

        return context


user_tax_letter_html = UserTaxLetterHtml.as_view()


class UserTaxLetter(PDFTemplateView):

    filename = 'tax_letter.pdf'
    template_name = 'account/tax-letter.html'

    def get_context_data(self, **kwargs):
        context = super(UserTaxLetter, self).get_context_data(**kwargs)
        customer = self.request.user.customer
        customer_charges = self.request.user.get_donations()
        charges_value = 0
        deductable_value = 0
        for charge in customer_charges:
            charges_value += charge.amount
        for charge in customer_charges:
            deductable_value += charge.deductable_amount
        if deductable_value == 0 and charges_value > 0:
            deductable_value = charges_value
        context['customer'] = customer
        context['charges_value'] = charges_value
        context['deductable_value'] = deductable_value
        context['year'] = timezone.now().year
        return context


user_tax_letter = UserTaxLetter.as_view()


class EmailConfirmedView(TemplateView):
    template_name = 'account/email_confirmed.html'


email_confirmed = EmailConfirmedView.as_view()


class EmailConfirmedDonateView(TemplateView):
    template_name = 'account/email_confirmed_donate.html'


email_confirmed_donate = EmailConfirmedDonateView.as_view()


class EmailConfirmedCatalogView(TemplateView):

    template_name = 'account/email_confirmed_catalog.html'

    def get_context_data(self, **kwargs):
        """Set next url so that the button can lead the user to the original location"""
        context = super(EmailConfirmedCatalogView, self).get_context_data(**kwargs)

        next_url = self.request.GET.get('next')
        if next:
            product_id = self.request.GET.get('product_id')
            if product_id:
                next_url += 'product_id=' + product_id
            context['next_url'] = next_url

        return context

email_confirmed_catalog = EmailConfirmedCatalogView.as_view()


class LoginView(CoreLoginView):

    def get_template_names(self):
        if self.request.is_ajax():
            return ["account/ajax_login.html"]
        else:
            return ["account/login.html"]

    def form_valid(self, form):
        result = super(LoginView, self).form_valid(form)

        # We need to delete every item in the basket except tickets
        # when the user logs in to avoid remembering any catalog items
        # that might have been left over.
        # The only case when a user is not authenticated and they add
        # items to the basket, and then they can log in, is tickets purchases.
        if self.request.user.is_authenticated():
            basket = self.request.basket
            basket.lines.exclude(product__product_class__name='Ticket').delete()

        return result


login_view = LoginView.as_view()


class EmailConfirmResendAjaxView(View):

    def post(self, request, *args, **kwargs):

        email = request.POST['email']
        try:
            email_address = SmallsEmailAddress.objects.get(
                user=request.user,
                email=email,
            )
            email_address.send_confirmation(request)
            response = json.dumps({'success': True})
        except SmallsEmailAddress.DoesNotExist:
            response = json.dumps({'success': False,
                                   'message': "Email address not found"})

        return HttpResponse(response, content_type="application/json")


email_confirm_resend_ajax = EmailConfirmResendAjaxView.as_view()


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
            messages.error(
                self.request, 'You need to be an artist to access that part of the site.')
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
    queryset = SmallsEmailAddress.objects.order_by('email')

    def get_context_data(self, **kwargs):
        context = super(ResendEmailConfirmationView,
                        self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        context = {'object_list': {}, }
        # if form.is_valid():
        #     return self.form_valid(form)
        # else:
        #     return self.form_invalid(form)
        return context


admin_email_confirmation = ResendEmailConfirmationView.as_view()
