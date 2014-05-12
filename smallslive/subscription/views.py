from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, RedirectView, ListView
from exceptions import PayPalError
from facade import confirm_transaction, fetch_transaction_details, get_paypal_url
from models import Subscription, UserSubscription, Feature
from django.utils.translation import ugettext as _


class SubscriptionListView(ListView):
    model = Subscription
    context_object_name = 'plans'

    def get_context_data(self, **kwargs):
        context = super(SubscriptionListView, self).get_context_data(**kwargs)
        context['features'] = Feature.objects.all(),
        return context


class SubscriptionDetailView(DetailView):
    model = Subscription


class PayPalRedirectView(RedirectView, DetailView):
    """
    Initiate the transaction with Paypal and redirect the user
    to PayPal's Express Checkout to perform the transaction.
    """
    model = Subscription
    permanent = False

    def get_redirect_url(self, **kwargs):
        try:
            return self._get_redirect_url(**kwargs)
        except PayPalError:
            messages.error(self.request, _(u"An error occurred communicating with PayPal"))
            url = reverse('admin:plans', current_app='subscription')
            return url

    def _get_redirect_url(self, **kwargs):
        object = self.get_object()
        if not object:
            messages.error(self.request, _(u"Your subscription is empty"))
            return reverse('admin:plans', current_app='subscription')
        params = {'subscription': object}

        user = self.request.user

        if settings.DEBUG:
            # Determine the localserver's hostname to use when
            # in testing mode
            params['host'] = self.request.META['HTTP_HOST']
        params['scheme'] = 'http'

        if user.is_authenticated():
            params['user'] = user

        return get_paypal_url(**params)


class CancelResponseView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        messages.error(self.request, _(u"PayPal transaction cancelled"))
        return reverse('admin:plans', current_app='subscription')


class SuccessResponseView(DetailView):
    template_name = 'subscription/preview.html'
    preview = True
    model = Subscription

    def get(self, request, *args, **kwargs):
        """
        Fetch details about the successful transaction from
        PayPal.  We use these details to show a preview of
        the order with a 'submit' button to place it.
        """
        try:
            token = request.GET['token']
        except KeyError:
            # Manipulation - redirect to basket page with warning message
            messages.error(self.request, _(u"Unable to determine PayPal transaction details"))
            return HttpResponseRedirect(reverse('admin:plans', current_app='subscription'))

        try:
            self.fetch_paypal_data(token)
        except PayPalError:
            messages.error(self.request, _(u"A problem occurred communicating with PayPal - please try again later"))
            return HttpResponseRedirect(reverse('admin:plans', current_app='subscription'))
        return super(SuccessResponseView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Place an order.

        We fetch the txn details again and then proceed with MSS standard
        payment details view for placing the order.
        """
        try:
            payer_id = request.POST['payer_id']
            token = request.POST['token']
        except KeyError:
            # Probably suspicious manipulation if we get here
            messages.error(self.request, _(u"A problem occurred communicating with PayPal - please try again later"))
            return HttpResponseRedirect(reverse('admin:plans', current_app='subscription'))
        try:
            self.fetch_paypal_data(token, payer_id)
        except PayPalError:
            # Unable to fetch txn details from PayPal - we have to bail out
            messages.error(self.request, _(u"A problem occurred communicating with PayPal - please try again later"))
            return HttpResponseRedirect(reverse('admin:plans', current_app='subscription'))

        return self.handle_payment(self.get_object())

    def fetch_paypal_data(self, token, payer_id = None):
        self.token = token
        if payer_id:
            self.payer_id = payer_id
        else:
            self.txn = fetch_transaction_details(token)
            self.payer_id = self.txn.profile_id

    def get_context_data(self, **kwargs):
        ctx = super(SuccessResponseView, self).get_context_data(**kwargs)
        if not hasattr(self, 'payer_id'):
            return ctx
        ctx.update({
            'payer_id': self.payer_id,
            'token': self.token,
            'paypal_user_email': self.txn.value('EMAIL'),
            'paypal_amount': Decimal(self.txn.value('AMT')),
        })
        # We convert the PayPal response values into those that match mss normal
        # context so we can re-use the preview template as is
        ctx['order_total'] = Decimal(self.txn.value('PAYMENTREQUEST_0_AMT'))

        return ctx

    def handle_payment(self, subscription):
        """
        Complete payment with PayPal - this calls the 'DoExpressCheckout'
        method to capture the money from the initial transaction.
        """
        try:
            payer_id = self.request.POST['payer_id']
            token = self.request.POST['token']
        except KeyError:
            messages.error(self.request, _(u"Unable to determine PayPal transaction details"))
            return HttpResponseRedirect(reverse('subscription:list', current_app='subscription'))
        try:
            txn = confirm_transaction(subscription, payer_id, token,
                                      currency=getattr(settings, 'SITE_CURRENCY', 'USD'))
        except PayPalError:
            messages.error(self.request, _(u"Unable to take payment"))
            return HttpResponseRedirect(reverse('subscription:list', current_app='subscription'))

        if not txn.is_successful:
            messages.error(self.request, _(u"Unable to take payment"))
            return HttpResponseRedirect(reverse('subscription:list', current_app='subscription'))

        # add user to group
        usr = UserSubscription.objects.get_site().filter(user=self.request.user)
        for us in usr:
            us.active = False
            us.save()
        subscription.group.user_set.add(self.request.user)
        us, created = UserSubscription.objects.get_or_create(subscription=subscription, user=self.request.user)
        us.extend()
        us.subscribe()
        messages.success(self.request, _(u"Your subscription has been updated!"))

        return HttpResponseRedirect(reverse('home'))
