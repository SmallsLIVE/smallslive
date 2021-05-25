import csv
import stripe
import traceback
from allauth.account.views import _ajax_response
from braces.views import FormValidMessageMixin, LoginRequiredMixin, StaffuserRequiredMixin
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django_filters.views import FilterView
from django.forms.models import model_to_dict
from django.http import StreamingHttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import TemplateView, FormView, ListView, View
from djstripe.models import Customer, Charge, Plan
from djstripe.settings import subscriber_request_callback
from djstripe.views import SyncHistoryView, ChangeCardView, ChangePlanView, \
    CancelSubscriptionView as BaseCancelSubscriptionView
from oscar.apps.payment.models import SourceType, Source
from oscar.core.loading import get_class
from oscar_apps.catalogue.mixins import ProductMixin
from oscar_apps.catalogue.models import Product
from oscar_apps.checkout.forms import PaymentForm, BillingAddressForm
from oscar_apps.partner.strategy import Selector
from oscar_apps.payment.exceptions import RedirectRequiredAjax
from artists.models import Artist
from events.models import Event
from users.models import SmallsUser
from users.utils import custom_send_receipt
from .filters import SponsorFilter, SupporterFilter
from .forms import ReactivateSubscriptionForm
from .mixins import PayPalMixin, StripeMixin
from .models import Donation

BankcardForm = get_class('payment.forms', 'BankcardForm')


class PaymentInfoView(TemplateView):
    """
    Shows payment form with options. Typically credit card form and PayPal.
    Shows billing address form. Uses Oscar for storing billing address.
    """

    def get_template_names(self):
        if self.request.is_ajax():
            if self.request.user.is_authenticated():
                template_name = 'subscriptions/supporter_step_donation_payment_info.html'
            else:
                template_name = 'subscriptions/supporter_step_anonymous_donation_payment_info.html'
        else:
            pass
        return [template_name]

    def get_authenticated_context(self):
        context = {
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        }

        billing_address_form = BillingAddressForm(None, self.request.user,
                                                  initial=self.get_billing_initial())
        context['billing_address_form'] = billing_address_form
        context['payment_form'] = PaymentForm(self.request.user, settings.STRIPE_SECRET_KEY)

        return context

    def get_anonymous_context(self):

        context = {
            'bankard_form': BankcardForm()
        }

        return context

    def get_context_data(self, **kwargs):
        context = super(PaymentInfoView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            context.update(self.get_authenticated_context())
        else:
            context.update(self.get_anonymous_context())

        return context

    def get_billing_initial(self):
        address = self.get_default_billing_address()
        if not address:
            address = self.request.user.addresses.first()

        if address:
            initial = model_to_dict(address)
            return initial
        else:
            return None

    def get_default_billing_address(self):
        if not self.request.user.is_authenticated():
            return None
        try:
            return self.request.user.addresses.get(is_default_for_billing=True)
        except:
            try:
                return self.request.user.addresses.first()
            except:
                return None


payment_info = PaymentInfoView.as_view()


class DonationPreviewView(TemplateView):
    """
    Shows donation preview (monthly or  one time)
    """

    def get_template_names(self):
        if self.request.is_ajax():
            template_name = 'subscriptions/supporter_step_donation_preview.html'
        else:
            pass
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super(DonationPreviewView, self).get_context_data(**kwargs)
        context['donation_type'] = self.request.GET.get('type')
        context['donation_amount'] = self.request.GET.get('amount')

        payment_method = self.request.GET.get('payment_method')
        context['payment_method'] = payment_method
        if payment_method == 'existing-credit-card':
            last = self.request.user.customer.card_last_4
            context['last_4'] = last
        elif payment_method == 'credit-card':
            last = self.request.GET.get('last')
            context['last_4'] = last

        # billing
        context['billing_first_name'] = self.request.GET.get('first_name')
        context['billing_last_name'] = self.request.GET.get('last_name')
        context['billing_line1'] = self.request.GET.get('line1')
        context['billing_line2'] = self.request.GET.get('line2')
        context['billing_city'] = self.request.GET.get('line4')
        context['billing_state'] = self.request.GET.get('state')
        context['billing_country'] = self.request.GET.get('country')

        return context


donation_preview = DonationPreviewView.as_view()


class ExecutePayPalPaymentView(PayPalMixin, View):
    """
    Receives the callback from PayPal in order to execute the payment.
    """

    def __init__(self):
        self.event = None
        self.order = None
        self.tickets_type = None

    def get(self, request, *args, **kwargs):
        """
        Receive callback from PayPal after the user has authorized the payment there.
        GET /store/checkout/paypal/execute/?paymentId=PAY-1LV98277E5422594XLP4E2MY&token=EC-1FB41424NL964725H&PayerID=EXH9W7JL6NSN8
        Confirm the payment and place the order
        """

        # Access will be granted in Complete view if payment_id matches.
        payment_id = self.execute_payment()
        # Check if payment id belongs to a Catalog donation -> product_id is set
        donation = Donation.objects.confirm_by_reference(payment_id)

        flow_type = 'one_time'
        url = reverse('become_supporter_complete') + \
            '?payment_id={}'.format(payment_id)
        if donation.product_id:
            flow_type ='product_support'
            url += '&flow_type={}&product_id={}'.format(flow_type, donation.product_id)
        if donation.sponsored_event_dedication:
            flow_type = 'event_sponsorship'
            url += '&flow_type={}&event_id={}'.format(flow_type, donation.sponsored_event_id)

        if flow_type == 'event_sponsorship':
            custom_send_receipt(receipt_type=flow_type,
                                amount=donation.amount, user=donation.user,
                                dedication=donation.sponsored_event_dedication,
                                musician=donation.sponsored_event.leader_string(),
                                event_date=donation.sponsored_event.get_date())
        else:
            custom_send_receipt(receipt_type='one_time',
                                amount=donation.amount, user=donation.user)

        return redirect(url)


supporter_paypal_execute = ExecutePayPalPaymentView.as_view()


class BecomeSupporterView(PayPalMixin, StripeMixin, TemplateView):

    template_name = 'subscriptions/become-supporter.html'

    def __init__(self, *args, **kwargs):
        self.amount = None
        self.deductable_amount = None
        self.bitcoin = False
        self.check = False
        self.event = None
        self.event_id = None
        self.sponsored_event_id = None
        self.sponsored_event_dedication = ''
        self.event_slug = None
        self.event_title = ''
        self.existing_cc = None
        self.flow_type = ''
        self.plan_type = None
        self.artist_id = None
        self.artist_full_name = None
        self.product_id = None
        self.product_title = ''
        self.stripe_token = None
        self.tickets_type = None
        self.paypal_credit_card = None
        super(BecomeSupporterView, self).__init__(*args, **kwargs)

    def get_artist_context(self):

        artist_id = self.request.GET.get('artist_id')
        if not artist_id:
            return {}
        full_name = Artist.objects.get(pk=artist_id).full_name
        context = {
            'artist_id': artist_id,
            'full_name': full_name
        }

        self.artist_id = artist_id
        self.artist_full_name = full_name

        return context

    def get_product_context(self):
        product_id = self.request.GET.get('product_id')
        if not product_id:
            return {}
        title = Product.objects.get(pk=product_id).title
        context = {
            'product_id': product_id,
            'product_title': title
        }

        self.product_id = product_id
        self.product_title = title

        return context

    def set_product(self):
        product_id = self.request.POST.get('product_id')
        if not product_id:
            return
        title = Product.objects.get(pk=product_id).title
        self.product_id = product_id
        self.product_title = title

    def get_event_context(self):
        event_id = self.request.GET.get('event_id')
        if not event_id:
            return {}

        event = Event.objects.get(pk=event_id)
        title = event.title
        slug = event.slug

        context = {
            'event': event,
            'event_artists': event.get_artists_info_dict(),
            'comma_separated_artists': event.get_performer_strings()
        }

        self.event = event
        self.event_id = event_id
        self.event_slug = slug
        self.event_title = title

        return context

    def set_artist(self):
        artist_id = self.request.POST.get('artist_id')
        if not artist_id:
            return

        artist = Artist.objects.get(pk=artist_id)
        self.artist_id = artist_id
        self.artist_full_name = artist.full_name()

    def set_event(self):
        event_id = self.request.POST.get('event_id')
        if not event_id:
            return

        event = Event.objects.get(pk=event_id)
        title = event.title
        slug = event.slug
        self.event = event
        self.event_id = event_id
        self.event_slug = slug
        self.event_title = title

    def set_sponsorship(self):
        if self.flow_type == 'event_sponsorship':
            event_id = self.request.POST.get('sponsored_event_id')
            self.sponsored_event_id = event_id
            self.sponsored_event_dedication = self.request.POST.get('dedication')
            self.event_id = None

    def set_attributes(self):

        self.flow_type = self.request.POST.get('flow_type', 'become_supporter')
        self.stripe_token = self.request.POST.get('stripe_token')
        self.plan_type = self.request.POST.get('type')
        self.amount = self.request.POST.get('amount')
        payment_method = self.request.POST.get('payment_method')
        self.existing_cc = payment_method == 'existing-credit-card'
        self.bitcoin = payment_method == 'bitcoin'
        self.check = payment_method == 'check'
        self.paypal_credit_card = payment_method == 'paypal-credit-card'
        if payment_method == 'paypal':
            self.stripe_token = None
            self.existing_cc = None

    def set_billing_address(self):

        billing_address_form = BillingAddressForm(
            None, self.request.user, self.request.POST)
        billing_address_form.fields['billing_option'].required = False
        # Must be valid or would have failed on the previous step.
        if billing_address_form.is_valid():
            billing_address_form.save()

    def get_context_data(self, **kwargs):

        current_user = self.request.user

        context = super(BecomeSupporterView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        context['payment_info_url'] = reverse('payment_info')
        context['donation_preview_url'] = reverse('donation_preview')
        context['form_action'] = reverse('become_supporter')
        context['flow_type'] = self.request.POST.get('flow_type') or self.request.GET.get(
            'flow_type', 'become_supporter')
        artist_context = self.get_artist_context()
        context.update(artist_context)
        product_context = self.get_product_context()
        context.update(product_context)
        event_context = self.get_event_context()
        context.update(event_context)

        if not current_user.is_anonymous():
            context['can_free_donate'] = current_user.get_donation_amount >= 100
        else:
            context['can_free_donate'] = False

        if not self.request.user.is_authenticated():
            context['flow_type'] = 'one_time_donation'
        else:
            # Whatever the flow type is, it needs to be become a supporter if the user
            # is not a supporter yet. They can't donate or get stuff from the Catalog.
            # Except if they are getting tickets
            if not current_user.can_watch_video and not context['flow_type'] == "ticket_support":
                context['flow_type'] = 'become_supporter'

            # We need to clear the basket in case the user has anything in there.
            # Except for tickets
            if not context['flow_type'] == 'ticket_support':
                self.request.basket.flush()

            context['gifts'] = []
            context['costs'] = []
            for product in Product.objects.filter(categories__name='Gifts'):
                context['gifts'].append(product)
                if product.variants.count():
                    context['costs'].append(
                        product.variants.first().stockrecords.first().cost_price)
                else:
                    context['costs'].append(
                        product.stockrecords.first().cost_price)

            def get_product_price(x):
                selector = Selector()
                strategy = selector.strategy(
                    request=self.request, user=self.request.user)

                if x.variants.count():
                    price = strategy.fetch_for_product(product=x.variants.first()).price.incl_tax
                else:
                    price = strategy.fetch_for_product(product=x).price.incl_tax

                return price

            context['gifts'].sort(
                key=lambda x: get_product_price(x))

        # Don't skip intro if user is not active. We need to force them to stay
        # on the Intro page with the "Confirm Email" button.
        if not (current_user.is_authenticated() and not current_user.has_activated_account):
            context['skip_intro'] = self.request.GET.get('skip_intro')

        context['min_donation'] = 10

        return context

    def execute_bitcoin_payment(self):
        donation = {
            'user': self.request.user,
            'currency': 'USD',
            'amount': self.amount,
            'payment_source': 'BitCoin',
            'confirmed': False,
            'artist_id': self.artist_id,
            'product_id': self.product_id,
            'event_id': self.event_id,
        }
        Donation.objects.create(**donation)

    def execute_check_payment(self):
        donation = {
            'user': self.request.user,
            'currency': 'USD',
            'amount': self.amount,
            'payment_source': 'Check',
            'confirmed': False,
            'artist_id': self.artist_id,
            'product_id': self.product_id,
            'event_id': self.event_id,
        }
        Donation.objects.create(**donation)

    def create_donation(self, payment_source=None,
                        reference=None, confirmed=True):

        user = None
        if self.request.user.is_authenticated():
            user = self.request.user

        donation_data = {
            'user': user,
            'currency': 'USD',
            'amount': self.amount,
            'deductable_amount': self.deductable_amount,
            'payment_source': payment_source,
            'reference': reference,
            'confirmed': confirmed,
            'artist_id': self.artist_id,
            'product_id': self.product_id,
            'event_id': self.event_id,
            'sponsored_event_id': self.sponsored_event_id,
            'sponsored_event_dedication': self.sponsored_event_dedication,
        }

        return Donation.objects.create(**donation_data)

    def post(self, request, *args, **kwargs):

        try:

            self.set_attributes()
            self.set_artist()
            self.set_product()
            self.set_event()
            self.set_sponsorship()
            self.set_billing_address()

            if self.existing_cc:
                stripe_customer = self.request.user.customer.stripe_customer
                self.stripe_token = stripe_customer.get('default_source')

            if self.amount:
                self.amount = int(self.amount)
                self.deductable_amount = self.amount

            if self.stripe_token:
                try:
                    # Donation will come through the webhook.
                    self.execute_stripe_payment()
                    url = reverse('become_supporter_complete') + \
                        "?flow_type=" + self.flow_type
                    if self.product_id:
                        url += '&product_id=' + self.product_id
                    if self.event_id:
                        url += '&event_id=' + self.event_id
                        url += '&event_slug=' + self.event_slug
                    if self.sponsored_event_id:
                        url += '&sponsored_event_id=' + self.sponsored_event_id
                        url += '&event_slug=' + self.event_slug
                        url += '&dedication=' + self.sponsored_event_dedication
                    if self.artist_id:
                        url += '&artist_id=' + self.artist_id

                    return _ajax_response(
                        self.request, redirect(url)
                    )
                except stripe.StripeError as e:
                    # add form error here
                    print traceback.format_exc()
                    return JsonResponse({'error': str(e)})
                except Exception as e:
                    print traceback.format_exc()
                    return JsonResponse({'error': str(e)})
            elif self.bitcoin:
                self.execute_bitcoin_payment()
                url = reverse('supporter_pending') + \
                    "?pending_payment_type=bitcoin"
                if self.product_id:
                    url += '&product_id=' + self.product_id
                if self.event_id:
                    url += '&event_id=' + self.event_id
                    url += '&event_slug=' + self.event_slug
                if self.artist_id:
                    url += '&artist_id=' + self.artist_id

                return _ajax_response(
                    self.request, redirect(url)
                )
            elif self.check:
                self.execute_check_payment()
                url = reverse('supporter_pending') + \
                    "?pending_payment_type=check"
                if self.product_id:
                    url += '&product_id=' + self.product_id
                if self.event_id:
                    url += '&event_id=' + self.event_id
                    url += '&event_slug=' + self.event_slug

                return _ajax_response(
                    self.request, redirect(url)
                )
            else:
                try:
                    payment_execute_url = self.request.build_absolute_uri(
                        reverse('supporter_paypal_execute'))
                    payment_cancel_url = self.request.build_absolute_uri(
                        reverse('become_supporter'))
                    item = {
                        'name': 'One Time Donation',
                        'price': self.amount,
                        "sku": "N/A",
                        'currency': 'USD',
                        'quantity': 1}
                    item_list = []
                    print 'call handle_paypal_payment ->'
                    self.handle_paypal_payment(
                        'USD', item_list,
                        execute_uri=payment_execute_url,
                        cancel_uri=payment_cancel_url
                    )
                except RedirectRequiredAjax as e:
                    self.create_donation(payment_source='PayPal Foundation',
                                         reference=e.reference, confirmed=False)
                    return JsonResponse({'payment_url': e.url})
        except Exception as e:
            message = str(e)
            return JsonResponse({'error': True, 'message': message})


become_supporter = BecomeSupporterView.as_view()


class BecomeSupporterCompleteView(BecomeSupporterView):
    """
    Registers or confirms donation and shows the Thank You page.
    Users can complete subscription by paying through PayPal or Stripe or
    by selecting a gift in the store or donating via Catalog.

    Recurring subscription: only Stripe ->
      There's no donation recorded

    One  Time Donation:  Stripe  ->
      Donation created and confirmed at the time of credit card charge.

    Gift: Stripe and PayPal ->
      Donations

    Project/Product (Catalog) Support ->
      Similar to One Time Donation


    """

    template_name = 'subscriptions/completed/thank_you.html'

    def set_context(self, context, payment_id):
        user = self.request.user

        source = Source.objects.filter(reference=payment_id).first()
        if source:
            order = source.order
            if order:
                # Orders have only one line always
                product = order.lines.first().product
                if product.misc_file:
                    file_product = product.misc_file.url
                    context['file_product'] = file_product
                if product.is_child:
                    product = product.parent
                    context['comma_separated_leaders'] = product.get_leader_strings()
                    context['album_product'] = product

                context['order'] = order

        return context

    def get_context_data(self, **kwargs):

        context = super(
            BecomeSupporterCompleteView, self
        ).get_context_data(**kwargs)
        context['completed'] = True
        context['flow_type'] = self.request.GET.get('flow_type') or context.get('flow_type')

        payment_id = self.request.GET.get('payment_id')
        product_id = self.request.GET.get('product_id')
        artist_id = self.request.GET.get('artist_id')
        sponsored_event_id = self.request.GET.get('sponsored_event_id')
        dedication = self.request.GET.get('dedication')
        if payment_id:
            context = self.set_context(context, payment_id)
        elif product_id:
            product = Product.objects.get(pk=product_id)
            context['album_product'] = product
        if artist_id:
            context['artist'] = Artist.objects.get(pk=artist_id)

        if sponsored_event_id:
            event = Event.objects.get(pk=sponsored_event_id)
            context['event'] = event
            context['dedication'] = dedication

        return context


become_supporter_complete = BecomeSupporterCompleteView.as_view()


class BecomeSupporterPendingView(BecomeSupporterView):

    def get_template_names(self):

        payment_type = self.request.GET.get('pending_payment_type')
        if payment_type == 'bitcoin':
            template_name = 'subscriptions/supporter-bitcoin-pending.html'
        elif payment_type == 'check':
            template_name = 'subscriptions/supporter-check-pending.html'

        return [template_name]


supporter_pending = BecomeSupporterPendingView.as_view()


class DonateView(BecomeSupporterView):

    template_name = 'subscriptions/donate.html'

    def get_context_data(self, **kwargs):

        context = super(DonateView, self).get_context_data(**kwargs)

        if self.request.GET.get('skip_intro'):
            context['skip_intro'] = True
        context['flow_type'] = 'one_time_donation'

        return context

donate = DonateView.as_view()


class EventSponsorshipView(BecomeSupporterView):

    template_name = 'subscriptions/event-sponsorship.html'

    def get_context_data(self, **kwargs):

        context = super(EventSponsorshipView, self).get_context_data(**kwargs)
        context['flow_type'] = 'event_sponsorship'
        context['dedication'] = self.request.GET.get('dedication')
        context['payment_info_url'] = reverse('payment_info')
        context['donation_preview_url'] = reverse('donation_preview')
        context['product_id'] = self.product_id
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        context['min_donation'] = context['event'].minimum_sponsorship_amount

        return context


event_sponsorship = EventSponsorshipView.as_view()


class ProductSupportView(ProductMixin, BecomeSupporterView):

    template_name = 'subscriptions/product-support.html'

    def get_context_data(self, **kwargs):

        context = super(ProductSupportView, self).get_context_data(**kwargs)
        context['flow_type'] = 'product_support'

        self.object = Product.objects.get(pk=kwargs.get('product_id'))
        self.get_products()

        # ctx['flow_type'] = 'catalog_selection'

        context['artist_with_media'] = self.artists_with_media
        context['active_card'] = self.active_card
        context['album_product'] = self.album_product
        context['comma_separated_leaders'] = self.object.get_leader_strings()

        context['payment_info_url'] = reverse('payment_info')
        context['donation_preview_url'] = reverse('donation_preview')
        context['product_id'] = self.object.pk
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY

        context['child_product'] = self.child_product
        context['gifts'] = self.gifts
        context['costs'] = self.costs

        return context


product_support = ProductSupportView.as_view()


class TicketSupportView(BecomeSupporterView):

    template_name = 'subscriptions/ticket-support.html'

    def get_event(self):

        basket = self.request.basket
        product = None
        for line in basket.lines.all():
            product = line.product

        if product:
            return product.event_set.event

    def can_use_existing_cc(self):
        return

    def get_context_data(self, **kwargs):

        context = super(TicketSupportView, self).get_context_data(**kwargs)
        context['payment_info_url'] = reverse('payment_info')
        context['donation_preview_url'] = reverse('donation_preview')
        event = self.get_event()
        if event:
            context['venue_name'] = event.get_venue_name()
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        context['can_use_existing_cc'] = self.request.user.can_use_existing_cc and event.is_foundation

        return context


ticket_support = TicketSupportView.as_view()


class SyncPaymentHistoryView(SyncHistoryView):
    template_name = 'account/blocks/payment_history.html'


sync_payment_history = SyncPaymentHistoryView.as_view()


class UpdateCardView(ChangeCardView):

    def get_post_success_url(self):
        return reverse('user_settings_new')

    def get(self, request, *args, **kwargs):
        # only POST
        return redirect(self.get_post_success_url())


update_card = UpdateCardView.as_view()


class CancelSubscriptionView(BaseCancelSubscriptionView):
    success_url = reverse_lazy("user_settings_new")


cancel_subscription = CancelSubscriptionView.as_view()


class UpdatePledgeView(BecomeSupporterView):

    def get_context_data(self, **kwargs):
        context = super(UpdatePledgeView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        context['form_action'] = reverse('become_supporter')
        context['flow_type'] = "update_pledge"
        return context


update_pledge = UpdatePledgeView.as_view()


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


class SupporterFilterQueryMixin(object):

    def get_queryset(self):

        order_by = self.request.GET.get('o', 'email')

        today = timezone.localtime(
            timezone.now().replace(hour=0, minute=0, second=0)).date()
        starting_day_of_current_year = today.replace(month=1, day=1)
        ending_day_of_current_year = today.replace(month=12, day=31)

        return SmallsUser.objects.filter(
            donations__date__gte=starting_day_of_current_year,
            donations__date__lte=ending_day_of_current_year,
            donations__confirmed=True
        ).distinct().order_by(order_by)


class SupporterFilterView(StaffuserRequiredMixin, SupporterFilterQueryMixin, FilterView):
    context_object_name = 'supporters'
    filterset_class = SupporterFilter
    paginate_by = 30
    template_name = 'subscriptions/supporter_list.html'

    def get_context_data(self, **kwargs):
        context = super(SupporterFilterView, self).get_context_data(**kwargs)
        paginator = context['paginator']
        page = paginator.page(self.request.GET.get('page', 1))
        adjacent_pages = 2
        start_page = max(page.number - adjacent_pages, 1)
        if start_page <= 3:
            start_page = 1
        end_page = page.number + adjacent_pages + 1
        if end_page >= paginator.num_pages - 1:
            end_page = paginator.num_pages + 1
        page_numbers = [n for n in xrange(start_page, end_page) if n > 0 and n <= paginator.num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': paginator.num_pages not in page_numbers,
        })

        return context


supporter_list = SupporterFilterView.as_view()


class SponsorFilterQueryMixin(object):

    def get_queryset(self):

        order_by = self.request.GET.get('o', 'date')

        return Donation.objects.filter(
            confirmed=True,
            sponsored_event__isnull=False
        ).select_related('user', 'event').order_by(order_by)


class SponsorFilterView(StaffuserRequiredMixin, SponsorFilterQueryMixin, FilterView):
    context_object_name = 'sponsors'
    filterset_class = SponsorFilter
    paginate_by = 30
    template_name = 'subscriptions/sponsor_list.html'

    def get_context_data(self, **kwargs):
        context = super(SponsorFilterView, self).get_context_data(**kwargs)
        paginator = context['paginator']
        page = paginator.page(self.request.GET.get('page', 1))
        adjacent_pages = 2
        start_page = max(page.number - adjacent_pages, 1)
        if start_page <= 3:
            start_page = 1
        end_page = page.number + adjacent_pages + 1
        if end_page >= paginator.num_pages - 1:
            end_page = paginator.num_pages + 1
        page_numbers = [n for n in xrange(start_page, end_page) if n > 0 and n <= paginator.num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': paginator.num_pages not in page_numbers,
        })

        return context

sponsor_list = SponsorFilterView.as_view()


class Echo:

    def write(self, value):
        return value

class SupporterListExport(StaffuserRequiredMixin, SupporterFilterQueryMixin, View):

    def get(self, request):

        def prepare(x):
            if isinstance(x, unicode):
                return x.encode('utf8')
            else:
                return x

        def add_donation_info(row):
            user_id = row[0]
            user = SmallsUser.objects.get(pk=user_id)
            return row + (user.get_donation_expiry_date, user.get_donation_amount)

        queryset = self.get_queryset().values_list('id', 'email', 'first_name', 'last_name')
        echo_buffer = Echo()
        csv_writer = csv.writer(echo_buffer)

        rows = (csv_writer.writerow([prepare(x) for idx, x in enumerate(add_donation_info(row)) if idx > 0]) for row in queryset)

        response = StreamingHttpResponse(rows, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="supporters.csv"'

        return response


supporter_list_export = SupporterListExport.as_view()
