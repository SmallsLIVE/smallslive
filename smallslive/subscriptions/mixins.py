from decimal import *
import paypalrestsdk
from paypal.payflow import facade
import stripe
from djstripe.models import Customer, Charge, Plan
from djstripe.settings import subscriber_request_callback
from oscar_stripe.facade import Facade
from django.conf import settings
from django.core.urlresolvers import reverse
from oscar.apps.payment.exceptions import RedirectRequired, \
    UnableToTakePayment, PaymentError
from oscar_apps.payment.exceptions import RedirectRequiredAjax
from subscriptions.models import Donation
from users.utils import charge, one_time_donation, \
    subscribe_to_plan, update_active_card


class PayPalMixin(object):

    def get_payment_data(self, item_list, currency, shipping_charge=0.00,
                         execute_uri=None, cancel_uri=None):

        subtotal = Decimal(self.amount)
        if shipping_charge:
            subtotal -= Decimal(shipping_charge)
        
        if not execute_uri:
            execute_uri = 'checkout:paypal_execute'
            cancel_uri = 'checkout:payment-details'

            payment_execute_url = self.request.build_absolute_uri(
                reverse(execute_uri))
            payment_cancel_url = self.request.build_absolute_uri(
                reverse(cancel_uri))
        else:
            payment_execute_url = execute_uri
            payment_cancel_url = cancel_uri

        data = {
            'intent': 'sale',
            'payer': {'payment_method': 'paypal'},

            'redirect_urls': {
                'return_url': payment_execute_url,
                'cancel_url': payment_cancel_url},
            'transactions': [{
                'item_list': {'items': item_list},
                'amount': {
                    'total': self.amount,
                    'currency': currency,
                    'details': {
                        'shipping': shipping_charge,
                        'subtotal': str(subtotal)
                    }
                },
                'description': 'SmallsLIVE'}]
        }

        return data

    def configure_paypal(self, venue=None):
        if venue:
            client_id = venue.get_paypal_client_id
            client_secret = venue.get_paypal_client_secret
        else:
            # Assume foundation
            client_id = settings.PAYPAL_CLIENT_ID
            client_secret = settings.PAYPAL_CLIENT_SECRET

        paypalrestsdk.configure({
            'mode': settings.PAYPAL_MODE,  # sandbox or live
            'client_id': client_id,
            'client_secret': client_secret})

    def handle_paypal_payment(self, currency, item_list,
                              donation=False,
                              deductable_total=0.00,
                              shipping_charge=0.00,
                              execute_uri=None,
                              cancel_uri=None):

        venue = self.request.basket.get_tickets_venue()
        self.configure_paypal(venue)

        payment_data = self.get_payment_data(item_list, currency, shipping_charge,
                                             execute_uri=execute_uri, cancel_uri=cancel_uri)

        payment = paypalrestsdk.Payment(payment_data)
        success = payment.create()
        if success:
            payment_id = payment.id
            for link in payment.links:
                if link.rel == 'approval_url':
                    # Convert to str to avoid Google App Engine Unicode issue
                    # https://github.com/paypal/rest-api-sdk-python/pull/58
                    approval_url = str(link.href)
            if self.request.is_ajax():
                raise RedirectRequiredAjax(approval_url, payment_id)
            else:
                raise RedirectRequired(approval_url)
        else:
            raise UnableToTakePayment(payment.error)

    def execute_payment(self, venue=None):
        self.configure_paypal(venue)
        payment_id = self.request.GET.get('paymentId')
        payer_id = self.request.GET.get('PayerID')
        payment = paypalrestsdk.Payment.find(payment_id)
        if not payment.execute({'payer_id': payer_id}):
            print(payment.error)  # Error Hash
            if  payment.error.get('name') != 'PAYMENT_ALREADY_DONE':
                raise UnableToTakePayment(payment.error)

        return payment_id

    def refund_paypal_payment(self, payment_id, total, currency, venue=None):
        self.configure_paypal(venue)
        payment = paypalrestsdk.Payment.find(payment_id)
        sale_id = payment.transactions[0].related_resources[0].sale.id
        sale = paypalrestsdk.Sale.find(sale_id)
        refund_data = {
            'amount': {
                'total': '%.2f' % float(total),
                'currency': currency
            }
        }
        print refund_data
        refund = sale.refund(refund_data)
        if refund.success():
            refund_id = refund.id
        else:
            print refund.error
            refund_id = 'Error: {}'.format(refund.error)[:64]

        return refund_id


class StripeMixin(object):

    def execute_stripe_payment(self):
        # As per Aslan's request
        # Yearly donations will no longer exist. They are One Time Donations  now.

        stripe_ref = None
        customer, created = Customer.get_or_create(
            subscriber=subscriber_request_callback(self.request))
        if self.plan_type == 'month':
            subscribe_to_plan(customer, self.stripe_token,
                              self.amount, self.plan_type, self.flow_type)
        else:
            stripe_ref = one_time_donation(
                customer, self.stripe_token, self.amount)
            if self.product_id:
                # We need to record the product id if donation comes from the Catalog.
                pass

        return stripe_ref

    def handle_stripe_payment(self, order_number, basket_lines, **kwargs):
        if self.request.user.is_authenticated():
            customer = self.request.user.customer
        else:
            customer = None
        venue = self.request.basket.get_tickets_venue()
        if not venue and customer:
            if not self.card_token.startswith('card_'):
                customer.update_card(self.card_token)
            charge = customer.charge(
                Decimal(
                    self.total.incl_tax if self.amount is None else self.amount.incl_tax),
                description=self.payment_description(order_number, self.total.incl_tax, **kwargs))
            stripe_ref = charge.stripe_id

        else:
            print 'stripe.charge ->'
            print 'Token: ', self.card_token
            resp = stripe.Charge.create(
                api_key=self.request.basket.get_tickets_venue().get_stripe_secret_key,
                source=self.card_token,
                amount=int(self.total.incl_tax * 100),  # Convert dollars into cents
                currency=settings.STRIPE_CURRENCY,
                description=self.payment_description(order_number, self.total.incl_tax, **kwargs),
            )
            print 'Resp: ', resp
            stripe_ref = resp['id']

        cost = 0
        for line in basket_lines:
            print line
            print dir(line)
            print line.stockrecord
            if line.stockrecord and line.stockrecord.cost_price:
                cost += line.stockrecord.cost_price

        return stripe_ref

    def refund_stripe_payment(self, charge_id, venue=None):
        if venue:
            api_key = venue.get_stripe_secret_key
        else:
            api_key = settings.STRIPE_SECRET_KEY
        charge = stripe.Charge.retrieve(api_key=api_key, id=charge_id)
        refund = charge.refund()

        return refund.id
