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
            if self.tickets_type == 'mezzrow':
                execute_uri = 'checkout:mezzrow_paypal_execute'
                cancel_uri = 'checkout:payment-details'
            else:
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

    def configure_paypal(self):
        if self.tickets_type == 'mezzrow':
            paypalrestsdk.configure({
                'mode': settings.PAYPAL_MODE,  # sandbox or live
                'client_id': settings.PAYPAL_MEZZROW_CLIENT_ID,
                'client_secret': settings.PAYPAL_MEZZROW_CLIENT_SECRET})
        else:
            paypalrestsdk.configure({
                'mode': settings.PAYPAL_MODE,  # sandbox or live
                'client_id': settings.PAYPAL_CLIENT_ID,
                'client_secret': settings.PAYPAL_CLIENT_SECRET})

    def handle_paypal_payment(self, currency, item_list,
                              donation=False,
                              deductable_total=0.00, shipping_charge=0.00,
                              execute_uri=None,
                              cancel_uri=None):

        self.configure_paypal()

        payment_data = self.get_payment_data(item_list, currency, shipping_charge,
                                             execute_uri=execute_uri, cancel_uri=cancel_uri)

        payment = paypalrestsdk.Payment(payment_data)
        success = payment.create()
        if success:
            payment_id = payment.id
            if donation:
                user = self.request.user
                if not user.is_authenticated():
                    user = None
                # Create Donation even though the payment is not yet authorized.
                donation = {
                    'user': user,
                    'currency': 'USD',
                    'amount': self.amount,
                    'reference': payment_id,
                    'confirmed': False,
                    'deductable_amount': str(deductable_total),
                    'product_id': self.product_id,
                    'event_id': self.event_id,
                }
                Donation.objects.create(**donation)

            for link in payment.links:
                if link.rel == 'approval_url':
                    # Convert to str to avoid Google App Engine Unicode issue
                    # https://github.com/paypal/rest-api-sdk-python/pull/58
                    approval_url = str(link.href)
                    print("Redirect for approval: %s" % approval_url)

            if self.request.is_ajax():
                raise RedirectRequiredAjax(approval_url)
            else:
                raise RedirectRequired(approval_url)
        else:
            raise UnableToTakePayment(payment.error)

    def handle_paypal_credit_card_payment(self):

        try:
            facade.sale(1, self.amount, self.bankcard)
        except Exception, e:
            ignore_error = getattr(settings, 'IGNORE_BANKCARD_PAYMENT_ERRORS', False)
            if not ignore_error:
                raise e

    def execute_payment(self):
        self.configure_paypal()
        payment_id = self.request.GET.get('paymentId')
        payer_id = self.request.GET.get('PayerID')
        payment = paypalrestsdk.Payment.find(payment_id)
        if not payment.execute({'payer_id': payer_id}):
            print(payment.error)  # Error Hash
            raise UnableToTakePayment(payment.error)

        return payment_id

    def refund_paypal_payment(self, payment_id, total, currency):
        self.configure_paypal()
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
                donation = {
                    'user': self.request.user,
                    'currency': 'USD',
                    'amount': self.amount,
                    'reference': stripe_ref,
                    'confirmed': False,
                    'product_id': self.product_id,
                    'event_id': self.event_id,
                }
                Donation.objects.create(**donation)

    def handle_stripe_payment(self, order_number, basket_lines, **kwargs):
        customer = self.request.user.customer
        if not self.card_token.startswith('card_'):
            customer.update_card(self.card_token)
            charge = customer.charge(
                Decimal(
                    self.total.incl_tax if self.amount is None else self.amount.incl_tax),
                description=self.payment_description(order_number, self.total.incl_tax, **kwargs))
            stripe_ref = charge.stripe_id

        else:
            stripe_ref = Facade().charge(
                order_number,
                self.total,
                card=self.card_token,
                description=self.payment_description(
                    order_number, self.total.incl_tax, **kwargs),
                metadata=self.payment_metadata(
                    order_number, self.total.incl_tax, basket_lines, **kwargs),
                customer=customer.stripe_id)

        cost = 0
        for line in basket_lines:
            print line
            print dir(line)
            print line.stockrecord
            if line.stockrecord and line.stockrecord.cost_price:
                cost += line.stockrecord.cost_price

        return stripe_ref

    def refund_stripe_payment(self, charge_id):
        charge = stripe.Charge.retrieve(id=charge_id)
        refund = charge.refund()

        return refund.id
