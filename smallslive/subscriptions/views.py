import stripe
from allauth.account.views import _ajax_response
from braces.views import FormValidMessageMixin, LoginRequiredMixin, StaffuserRequiredMixin

from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, ListView, View
from djstripe.mixins import SubscriptionMixin
from djstripe.models import Customer, Charge, Plan
from djstripe.settings import subscriber_request_callback
from djstripe.views import SyncHistoryView, ChangeCardView, ChangePlanView,\
    CancelSubscriptionView as BaseCancelSubscriptionView
from oscar_apps.catalogue.models import Product
from oscar_apps.checkout.forms import PaymentForm, BillingAddressForm
from oscar.apps.payment.exceptions import RedirectRequired, \
    UnableToTakePayment, PaymentError
from oscar_apps.payment.exceptions import RedirectRequiredAjax
from oscar_apps.partner.strategy import Selector
from oscar.apps.payment.models import SourceType, Source
from users.models import SmallsUser
from users.utils import charge, one_time_donation, \
    subscribe_to_plan,  update_active_card
from subscriptions.models import Donation
from .forms import PlanForm, ReactivateSubscriptionForm
from .mixins import PayPalMixin


class PaymentInfoView(TemplateView):
    """
    Shows payment form with options. Typically credit card form and PayPal.
    Shows billing address form. Uses Oscar for storing billing address.
    """
    def get_template_names(self):
        if self.request.is_ajax():
            template_name = 'partials/_payment_info.html'
        else:
            pass
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super(PaymentInfoView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY

        billing_address_form = BillingAddressForm(None, self.request.user,
                                                  initial=self.get_billing_initial())
        context['billing_address_form'] = billing_address_form
        context['payment_form'] = PaymentForm(self.request.user)


        return context

    def get_billing_initial(self):
        address = self.get_default_billing_address()
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
            return None

payment_info = PaymentInfoView.as_view()


class ExecutePayPalPaymentView(PayPalMixin, View):
    """
    Receives the callback from PayPal in order to execute the payment.
    """

    def get(self, request, *args, **kwargs):
        """
        Receive callback from PayPal after the user has authorized the payment there.
        GET /store/checkout/paypal/execute/?paymentId=PAY-1LV98277E5422594XLP4E2MY&token=EC-1FB41424NL964725H&PayerID=EXH9W7JL6NSN8
        Confirm the payment and place the order
        """

        # Access will be granted in Complete view if payment_id matches.
        payment_id = self.execute_payment()

        return redirect(reverse(
            'become_supporter_complete') + '?payment_id={}'.format(payment_id))


supporter_paypal_execute = ExecutePayPalPaymentView.as_view()


class ContributeFlowView(TemplateView):
    def get_template_names(self):
        if self.request.is_ajax():
            template_name = 'account/supporter-flow-ajax.html'
        else:
            template_name = 'account/supporter-flow.html'
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super(ContributeFlowView, self).get_context_data(**kwargs)
        return context


class BecomeSupporterView(ContributeFlowView, PayPalMixin):

    def get_context_data(self, **kwargs):
        context = super(BecomeSupporterView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        context['payment_info_url'] = reverse('payment_info')
        context['form_action'] = reverse('become_supporter')
        context['flow_type'] = self.request.GET.get('flow_type', "become_supporter")
        if not self.request.user.is_anonymous():
            context['can_free_donate'] = self.request.user.get_donation_amount >= 100 
        else: 
            context['can_free_donate'] = False
        print self.request.GET.get('flow_type', "become_supporter")

        # We need to clear the basket in case the user has anything in there.
        self.request.basket.flush()

        context['gifts'] = []
        context['costs'] = []
        selector = Selector()
        strategy = selector.strategy(request=self.request, user=self.request.user)
        for product in Product.objects.filter(product_class__slug='gift'):
            context['gifts'].append(product)
            if product.variants.count():
                context['costs'].append(product.variants.first().stockrecords.first().cost_price)
            else:
                context['costs'].append(product.stockrecords.first().cost_price)

        context['gifts'].sort(key=lambda x: strategy.fetch_for_product(product=x).price.incl_tax)

        return context

    def _handle_paypal_payment(self, amount, plan_type):
        print '***************'
        print 'Handle paypal payment:'
        payment_execute_url = self.request.build_absolute_uri(reverse('supporter_paypal_execute'))
        payment_cancel_url = self.request.build_absolute_uri(reverse('become_supporter'))
        print payment_execute_url
        item = {
            'name': 'One Time Donation',
            'price': amount,
            "sku": "N/A",
            'currency': 'USD',
            'quantity': 1}
        item_list = [item]
        self.handle_paypal_payment('USD', amount, item_list, donation=True)

    def execute_stripe_payment(self, stripe_token, amount, plan_type, flow_type):
        print '********************************'
        print 'execute stripe payment'
        print 'Amount: ', amount
        print 'Token: ', stripe_token

        # As per Aslan's request
        # Yearly donations will no longer exist. They are One Time Donations  now.
        customer, created = Customer.get_or_create(
            subscriber=subscriber_request_callback(self.request))
        if plan_type == 'month':
            subscribe_to_plan(customer, stripe_token, amount, plan_type, flow_type)
        else:
            one_time_donation(customer, stripe_token, amount, flow_type)

    def post(self, request, *args, **kwargs):
        flow_type = self.request.POST.get('flow_type', "become_supporter")
        print "FLOW"
        print flow_type
        print "FLOW"
        stripe_token = self.request.POST.get('stripe_token')
        plan_type = self.request.POST.get('type')
        amount = self.request.POST.get('quantity')
        existing_cc = self.request.POST.get('payment_method')
        if existing_cc:
            stripe_customer = self.request.user.customer.stripe_customer
            stripe_token = stripe_customer.get('default_source')

        if self.request.POST.get('stripe_token'):
            stripe_token = self.request.POST.get('stripe_token')

        if amount:
            amount = int(amount)

        if stripe_token:
            try:
                self.execute_stripe_payment(stripe_token, amount, plan_type, flow_type)
                return _ajax_response(
                    self.request, redirect(reverse('become_supporter_complete') + "?flow_type=" + flow_type)
                )
            except stripe.StripeError as e:
                # add form error here
                print e
                return JsonResponse({'error' :str(e)})
        else:
            try:
                self._handle_paypal_payment(amount, plan_type)
            except RedirectRequired as e:
                print 'Redirect required'
                return redirect(e.url)
            except RedirectRequiredAjax as e:
                print 'JsonResponse ....'
                return JsonResponse({'payment_url': e.url})


become_supporter = BecomeSupporterView.as_view()


class DonateView(BecomeSupporterView):
    def get_context_data(self, **kwargs):
        context = super(DonateView, self).get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        context['form_action'] = reverse('donate')
        context['redirect_url'] = self.request.META.get('HTTP_REFERER')
        context['flow_type'] = "donate"

        return context

    def post(self, request, *args, **kwargs):

        redirect_url = self.request.POST.get('redirect_url')

        paypal_payment_id = self.request.POST.get('paypal_payment_id')
        if paypal_payment_id:
            pass
        else:
            stripe_token = self.request.POST.get('stripe_token')
            amount = int(self.request.POST.get('quantity'))

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

        return context


donate_complete = DonateCompleteView.as_view()


class BecomeSupporterCompleteView(BecomeSupporterView):
    """
    Registers or confirms donation and shows the Thank You page.
    Users can complete subscription by paying through PayPal or Stripe or
    by selecting a gift in the store.

    Recurring subscription: only Stripe ->
      There's no donation recorded

    One  Time Donation:  Stripe  ->
      Donation created and confirmed at the time of credit card charge.

    Gift: Stripe and PayPal ->
      Donations



    """

    def get_context_data(self, **kwargs):
        print '*******************'
        print 'CompleteView: '

        user = self.request.user

        context = super(
            BecomeSupporterCompleteView, self
        ).get_context_data(**kwargs)
        context['completed'] = True

        payment_id = self.request.GET.get('payment_id')
        print payment_id
        if payment_id:
            # Donated directly  by PayPal or Stripe
            source = Donation.objects.filter(reference=payment_id).first()
            if source:
                source.confirmed = True
                source.save()
             # Donated by selecting a gift in the store
            else:
                source = Source.objects.filter(reference=payment_id).first()
                if source and user.is_authenticated():
                    # Create Donation
                    donation = {
                        'user': user,
                        'currency': source.currency,
                        'amount': source.amount_allocated,
                        'reference': payment_id,
                        'confirmed': True,

                    }
                    Donation.objects.create(**donation)

           
            
     
                

        if not payment_id or not source:
            context['error'] = 'We could not find your payment reference. Contact our support'

        return context


become_supporter_complete = BecomeSupporterCompleteView.as_view()


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
        return reverse('user_settings_new')

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
