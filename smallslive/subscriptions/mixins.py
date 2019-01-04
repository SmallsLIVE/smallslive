import paypalrestsdk
import stripe
from django.conf import settings
from django.core.urlresolvers import reverse
from oscar.apps.payment.exceptions import RedirectRequired, \
    UnableToTakePayment, PaymentError
from oscar_apps.payment.exceptions import RedirectRequiredAjax
from subscriptions.models import Donation


class PayPalMixin(object):

    def configure_paypal(self):
        paypalrestsdk.configure({
            'mode': settings.PAYPAL_MODE,  # sandbox or live
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET})

    def handle_paypal_payment(self, currency, total, item_list,
                              payment_execute_url, payment_cancel_url,
                              donation=False):
        print '******************************'
        print 'PayPal Mixin handle PayPal payment'

        print total
        print currency

        self.configure_paypal()

        print 'payment data'
        payment_data = {
            'intent': 'sale',
            'payer': {'payment_method': 'paypal'},
            'redirect_urls': {
                'return_url': payment_execute_url,
                'cancel_url': payment_cancel_url},
            'transactions': [{
                'item_list': {'items': item_list},
                'amount': {
                    'total': total,
                    'currency': currency},
                'description': 'SmallsLIVE'}]}
        print 'paypal restsdk'
        payment = paypalrestsdk.Payment(payment_data)
        print 'payment_id'
        payment_id = payment.create()
        print payment_id
        if payment_id:
            print donation
            if donation and self.request.user.is_authenticated():
                # Create Donation even though the payment is not yet authorized.
                donation = {
                    'user': self.request.user,
                    'currency': 'USD',
                    'amount': total,
                    'reference': payment_id
                }
                print donation
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
            print payment
            print payment.error
            raise UnableToTakePayment(payment.error)

    def execute_payment(self):

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

    def refund_stripe_payment(self, charge_id, total):
        charge = stripe.Charge.retrieve(id=charge_id)
        refund = charge.refund()

        return refund.id