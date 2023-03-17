from decimal import *
import paypalrestsdk
import stripe
from django.conf import settings
from django.urls import reverse
from djstripe.models import Customer, Charge, Plan
from djstripe.settings import subscriber_request_callback
from oscar.apps.payment.exceptions import RedirectRequired, \
    UnableToTakePayment, PaymentError
from oscar_apps.payment.exceptions import RedirectRequiredAjax
from users.utils import charge, one_time_donation, \
    subscribe_to_plan, update_active_card


class PaymentCredentialsMixin(object):

    def get_payment_accounts(self):

        if self.event:
            if self.event.is_foundation:
                is_foundation = True
            else:
                is_foundation = False
                venue = self.event.venue
                stripe_client_id = venue.get_stripe_publishable_key
                stripe_client_secret = venue.get_stripe_secret_key
                paypal_client_id = venue.get_paypal_client_id
                paypal_client_secret = venue.get_paypal_client_secret
        else:
            if self.order:
                item = self.order
            else:
                item = self.request.basket
            if item.has_catalog():
                is_foundation = False
                stripe_client_id = settings.STRIPE_FOR_PROFIT_PUBLISHABLE_KEY
                stripe_client_secret = settings.STRIPE_FOR_PROFIT_SECRET_KEY
                paypal_client_id = settings.PAYPAL_FOR_PROFIT_CLIENT_ID
                paypal_client_secret = settings.PAYPAL_FOR_PROFIT_CLIENT_SECRET
            else:
                is_foundation = True

        if is_foundation:
            stripe_client_id = settings.STRIPE_PUBLISHABLE_KEY
            stripe_client_secret = settings.STRIPE_SECRET_KEY
            paypal_client_id = settings.PAYPAL_CLIENT_ID
            paypal_client_secret = settings.PAYPAL_CLIENT_SECRET

        return is_foundation, stripe_client_id, stripe_client_secret, \
               paypal_client_id, paypal_client_secret

    def get_stripe_payment_credentials(self):
        data = self.get_payment_accounts()
        return data[0], data[1], data[2]

    def get_paypal_payment_credentials(self):
        data = self.get_payment_accounts()
        return data[0], data[3], data[4]


class PayPalMixin(PaymentCredentialsMixin):


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
                'amount': {
                    'total': self.amount,
                    'currency': currency,
                    'details': {
                        'shipping': shipping_charge,
                        'subtotal': str(subtotal)
                    }
                },
                'description': 'SmallsLIVE Foundation'}]
        }
        if item_list:
            data['transactions'][0]['item_list'] = item_list

        return data

    def configure_paypal(self):
        is_foundation, client_id, client_secret = self.get_paypal_payment_credentials()
        data = {
            'mode': settings.PAYPAL_MODE,  # sandbox or live
            'client_id': client_id,
            'client_secret': client_secret
        }
        paypalrestsdk.configure(data)

    def handle_paypal_payment(self, currency, item_list,
                              shipping_charge=0.00,
                              execute_uri=None,
                              cancel_uri=None):
        self.configure_paypal()

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
            print(payment.error)
            raise UnableToTakePayment(payment.error)

    def execute_payment(self):
        self.configure_paypal()
        payment_id = self.request.GET.get('paymentId')
        payer_id = self.request.GET.get('PayerID')
        payment = paypalrestsdk.Payment.find(payment_id)
        if not payment.execute({'payer_id': payer_id}):
            print(payment.error)  # Error Hash
            if  payment.error.get('name') != 'PAYMENT_ALREADY_DONE':
                raise UnableToTakePayment(payment.error)

        return payment_id

    def refund_paypal_payment(self, payment_id, total, currency, order=None):
        self.order = order
        self.event = order.get_tickets_event()
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
        refund = sale.refund(refund_data)
        if refund.success():
            refund_id = refund.id
        else:
            print(refund.error)
            refund_id = 'Error: {}'.format(refund.error)[:64]

        return refund_id


class StripeMixin(PaymentCredentialsMixin):

    def execute_stripe_payment(self):
        # As per Aslan's request
        # Yearly donations will no longer exist. They are One Time Donations now.

        stripe_ref = None
        customer, created = Customer.get_or_create(
            subscriber=subscriber_request_callback(self.request))
        if self.plan_type == 'month':
            subscribe_to_plan(customer, self.stripe_token,
                              self.amount, self.plan_type, self.flow_type)
        else:
            event_id = None
            dedication = ''
            event_date = None
            musician = ''
            donation_type = 'one_time'
            if self.flow_type == 'event_sponsorship':
                event_id = self.sponsored_event_id
                dedication = self.sponsored_event_dedication
                musician = self.sponsored_event.leader_string()
                event_date = self.sponsored_event.get_date()
                donation_type = 'event_sponsorship'

            stripe_ref = one_time_donation(
                customer, self.stripe_token, self.amount, donation_type=donation_type,
                event_id=event_id, dedication=dedication, event_date=event_date, musician=musician)
            if self.product_id:
                # We need to record the product id if donation comes from the Catalog.
                pass

        return stripe_ref

    def handle_stripe_payment(self, order_number, basket_lines, **kwargs):

        if self.request.user.is_authenticated():
            customer = self.request.user.customer
        else:
            customer = None

        data = self.get_stripe_payment_credentials()
        is_foundation = data[0]
        stripe_secret_key = data[2]

        # Smalls tickets are accounted according to the venue's account.
        if customer and is_foundation:
            if not self.card_token.startswith('card_'):
                customer.update_card(self.card_token)
            charge = customer.charge(
                Decimal(
                    self.total.incl_tax if self.amount is None else self.amount.incl_tax),
                description=self.payment_description(order_number, self.total.incl_tax, **kwargs))
            stripe_ref = charge.stripe_id

        else:
            metadata = {}
            if not is_foundation:
                metadata = {
                    'isFoundation': False
                }
            resp = stripe.Charge.create(
                api_key=stripe_secret_key,
                source=self.card_token,
                amount=int(self.total.incl_tax * 100),  # Convert dollars into cents
                currency=settings.STRIPE_CURRENCY,
                description=self.payment_description(order_number, self.total.incl_tax, **kwargs),
                metadata=metadata
            )
            stripe_ref = resp['id']

        cost = 0
        for line in basket_lines:
            if line.stockrecord and line.stockrecord.cost_price:
                cost += line.stockrecord.cost_price

        return stripe_ref

    def refund_stripe_payment(self, charge_id, order=None):
        self.order = order
        self.event = order.get_tickets_event()
        api_key = self.get_stripe_payment_credentials()[2]
        charge = stripe.Charge.retrieve(api_key=api_key, id=charge_id)
        refund = charge.refund()

        return refund.id
