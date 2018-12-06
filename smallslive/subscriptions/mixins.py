import paypalrestsdk
from django.conf import settings
from django.core.urlresolvers import reverse
from oscar.apps.payment.exceptions import RedirectRequired, \
    UnableToTakePayment, PaymentError
from oscar_apps.payment.exceptions import RedirectRequiredAjax
from subscriptions.models import Donation


class PayPalMixin(object):

    def handle_paypal_payment(self, currency, total, item_list,
                              payment_execute_url, payment_cancel_url,
                              donation=False):
        print '******************************'
        print 'PayPal Mixin handle PayPal payment'

        print total
        print currency

        paypalrestsdk.configure({
            'mode': settings.PAYPAL_MODE,  # sandbox or live
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET})

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
        payment = paypalrestsdk.Payment(payment_data)
        payment_id = payment.create()
        if payment_id:

            if donation:
                # Create Donation even though the payment is not yet authorized.
                donation = {
                    'user': self.request.user,
                    'currency': 'USD',
                    'amount': total,
                    'reference': payment_id
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

    def execute_payment(self):

        payment_id = self.request.GET.get('paymentId')
        payer_id = self.request.GET.get('PayerID')
        payment = paypalrestsdk.Payment.find(payment_id)
        if not payment.execute({'payer_id': payer_id}):
            print(payment.error)  # Error Hash
            raise UnableToTakePayment(payment.error)

        return payment_id
