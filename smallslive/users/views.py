from datetime import datetime, date
import json
import stripe
import logging
from wkhtmltopdf.views import PDFTemplateView
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import ObjectDoesNotExist
from django.views.generic import TemplateView, FormView, ListView, View
from django.utils import timezone
from allauth.account.app_settings import EmailVerificationMethod
from allauth.account.forms import ChangePasswordForm
from users.models import SmallsEmailAddress
from allauth.account.views import SignupView as AllauthSignupView, \
    LoginView as CoreLoginView, _ajax_response, \
    ConfirmEmailView as AllauthConfirmEmailView
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
from oscar_apps.order.models import PaymentEvent, Line, Order
from events.models import Event

from .utils import complete_signup, url_str_to_user_pk

from allauth.account.adapter import get_adapter
from allauth.account.utils import perform_login
from allauth.account import app_settings
from utils.utils import send_order_confirmation_email, send_order_refunded_email

logger = logging.getLogger(__name__)


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
        verification_method = EmailVerificationMethod.MANDATORY
        complete_signup(
            self.request, user, verification_method, self.get_success_url()
        )
        return HttpResponseRedirect(reverse('account_email_verification_sent'))


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
                request, "You've successfully updated your basic info.")
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
                request, 'Your email address has been changed successfully. Please check your email.')
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
        else:
            assert False, artist_info_form.errors
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
    customer = None
    customer_charges = None
    user_archive_access_until = None
    monthly_pledge_in_dollars = None
    cancel_at = None
    billing_address = None

    show_email_confirmation = False
    subscription = None

    try:
        if request.user.djstripe_customers.all():
            customer = request.user.djstripe_customers.all()[0]
    except:
        customer = None

    user_archive_access_until = None
    if request.user.has_archive_access:
        user_archive_access_until = request.user.get_archive_access_expiry_date()

    if customer and customer.has_any_active_subscription():
        if len(customer.subscriptions.all()) > 1:
            subscription = customer.subscriptions.all()[1]
        else:
            subscription = customer.subscriptions.all()[0]
        plan_id = subscription.plan
        try:
            plan = stripe.Plan.retrieve(id=plan_id)
        except stripe.error.InvalidRequestError:
            plan = None

    customer_charges = request.user.get_donations(this_year=False).order_by('-date')
    charges_value = 0
    for charge in customer_charges:
        if charge.amount:
            charges_value = charges_value + charge.amount

        artist_info_form = ArtistInfoForm(instance=request.user)

    customer_detail = None
    # @TODO : Fix later with djstripe
    #changes for new djstripe version 2.5
    
    if request.user.djstripe_customers.all():
            customer = request.user.djstripe_customers.all()[0]
    if customer and customer.id:
        customer_detail = CustomerDetail.get(
            id=customer.id)
        if len(customer.subscriptions.all()) > 1:
            subscription = customer.subscriptions.all()[1]
        elif len(customer.subscriptions.all()):
            subscription = customer.subscriptions.all()[0]
        else:
            subscription = None

    if customer_detail and subscription:
        monthly_pledge_in_dollars = subscription.plan.amount

    if customer_detail and subscription:
        date_format = '%d/%m/%y'
        today = datetime.now().strftime(date_format)
        period_end["date"] = subscription.current_period_end.strftime(date_format)
        period_end["due"] = subscription.current_period_end.strftime(date_format) <= today

    if customer_detail and subscription:
        cancel_at = subscription.cancel_at_period_end
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

    last4 = None
    exp_month = None
    exp_year = None
    if customer_detail and customer_detail.invoice_settings.default_payment_method:
        payment_method = stripe.PaymentMethod.retrieve(customer_detail.invoice_settings.default_payment_method)
        last4 = payment_method.card.last4
        exp_month = payment_method.card.exp_month
        exp_year = payment_method.card.exp_year

    return render(request, 'account/user_settings_new.html', {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'change_email_form': change_email_form,
        'change_profile_form': edit_profile_form,
        'change_password_form': change_password_form,
        'current_user': request.user,
        'artist_info_form': artist_info_form,
        'plan': plan,
        'donations': request.user.get_donations(this_year=False) or None,
        'customer_detail': customer_detail or '',
        'customer': customer or '',
        'subscription': subscription or '',
        'customer_charges': customer_charges or '',
        'charges_value': request.user.get_donation_amount or '0',
        'period_end': period_end,
        'user_archive_access_until': user_archive_access_until,
        'monthly_pledge_in_dollars': monthly_pledge_in_dollars or 'no',
        'cancelled': cancel_at or '',
        'donate_url': reverse('donate'),
        'billing_address': billing_address or '',
        'show_email_confirmation_dialog': show_email_confirmation,
        'last4': last4 or None,
        'exp_month': exp_month or None,
        'exp_year': exp_year or None,
    })


def check_account_status(request):
    user = request.user
    is_authenticated = user.is_authenticated
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
        customer = None
        try:
            if self.request.user.djstripe_customers.all():
                customer = self.request.user.djstripe_customers.all()[0]
        except:
            customer = None
        year = self.request.GET.get('year', str(timezone.now().year))
        year = int(year)
        customer_charges = customer.subscriber.get_donations(year=year)
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
        context['year'] = year

        return context


user_tax_letter_html = UserTaxLetterHtml.as_view()


class UserTaxLetter(PDFTemplateView):

    filename = 'tax_letter.pdf'
    template_name = 'account/tax-letter.html'

    def get_context_data(self, **kwargs):
        context = super(UserTaxLetter, self).get_context_data(**kwargs)
        customer = None
        try:
            if self.request.user.djstripe_customers.all():
                customer = self.request.user.djstripe_customers.all()[0]
        except:
            customer = None
        year = self.request.GET.get('year', str(timezone.now().year))
        year = int(year)
        customer_charges = self.request.user.get_donations(year=year)
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
        context['year'] = year

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
        if self.request.user.is_authenticated:
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
        self.logged_in = user.is_authenticated
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
        self.logged_in = user.is_authenticated
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

class ConfirmEmailView(AllauthConfirmEmailView):

    def login_on_confirm(self, confirmation):
        """
        Simply logging in the user may become a security issue. If you
        do not take proper care (e.g. don't purge used email
        confirmations), a malicious person that got hold of the link
        will be able to login over and over again and the user is
        unable to do anything about it. Even restoring their own mailbox
        security will not help, as the links will still work. For
        password reset this is different, this mechanism works only as
        long as the attacker has access to the mailbox. If they no
        longer has access they cannot issue a password request and
        intercept it. Furthermore, all places where the links are
        listed (log files, but even Google Analytics) all of a sudden
        need to be secured. Purging the email confirmation once
        confirmed changes the behavior -- users will not be able to
        repeatedly confirm (in case they forgot that they already
        clicked the mail).

        All in all, opted for storing the user that is in the process
        of signing up in the session to avoid all of the above.  This
        may not 100% work in case the user closes the browser (and the
        session gets lost), but at least we're secure.
        """
        user_pk = None
        user_pk_str = get_adapter(self.request).unstash_user(self.request)
        if user_pk_str:
            user_pk = url_str_to_user_pk(user_pk_str)
        user = confirmation.email_address.user
        if user_pk == user.pk and self.request.user.is_anonymous:
            return perform_login(self.request,
                                 user,
                                 app_settings.EmailVerificationMethod.NONE,
                                 # passed as callable, as this method
                                 # depends on the authenticated state
                                 redirect_url=self.get_redirect_url)

        return None
custom_confirm_email = ConfirmEmailView.as_view()

class EmailVerificationSentView(TemplateView):
    template_name = 'account/verification_sent.html'

email_verification_sent = EmailVerificationSentView.as_view()


class ResendConfirmationEmail(View):

    def resend_confirmation_email(self, order, email):
        message = {}
        event_info = order.basket.get_tickets_event()
        message['order_number'] = order.number
        message['party_name'] = order.first_name + ' ' + order.last_name
        message['event_title'] = event_info.title
        message['event_date'] = event_info.date
        message['venue'] = event_info.get_venue_name()
        for line in order.lines.all():
            message['quantity'] = line.quantity
            message['total_amount'] = line.line_price_incl_tax
            message['time'] = line.product.event_set.start
        send_order_confirmation_email(email, message)

    def resend_refund_email(self, order, email):
        line = order.lines.first()
        payment_event = PaymentEvent.objects.filter(order=order)

        payment_event = payment_event.filter(event_type__code='refunded') \
                        | payment_event.filter(event_type__code='partialrefund')
        payment_event = payment_event.order_by('-date_created').first()

        if not payment_event:
            raise ValueError("No refund available for this order")

        payment_event_quantity = payment_event.line_quantities.first()

        message = {}
        message['order_number'] = order.number
        message['refund_amount'] = payment_event.amount
        message['refund_quantity'] = payment_event_quantity.quantity if payment_event_quantity else ''
        if line:
            if line.product.event_set.event_id:
                product_event = Event.objects.get(id=line.product.event_set.event_id)
                message['event_date'] = product_event.date

            message['event_title'] = line.title
            message['quantity'] = line.quantity
            message['time'] = line.product.event_set.start

        send_order_refunded_email(email, message)

    def post(self, request):
        email_type = request.POST['resend_type']
        customer_email = request.POST['email']
        order_number = request.POST['order_number']
        try:
            order = Order.objects.get(number=order_number)
            if email_type == 'confirmation':
                self.resend_confirmation_email(order, customer_email)
            elif email_type == 'refund':
                self.resend_refund_email(order, customer_email)
            return JsonResponse({
                'status': 'success'
            }, status=200)

        except Exception as E:
            logger.error(str(E), exc_info=True)

        return JsonResponse({
            'status': 'error'
        }, status=500)
