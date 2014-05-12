"""
Responsible for briding between MSS and the PayPal gateway
"""
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings
from gateway import (
    set_txn, get_txn, do_txn_recurring)


SITE_CURRENCY = getattr(settings, 'SITE_CURRENCY', 'USD')


def get_paypal_url(subscription, user=None, host=None, scheme='https'):
    """
    Return the URL for PayPal Express transaction.

    This involves registering the txn with PayPal to get a one-time
    URL.  If a shipping method and shipping address are passed, then these are
    given to PayPal directly - this is used within when using PayPal as a
    payment method.
    """
    currency = SITE_CURRENCY
    if host is None:
        host = Site.objects.get_current().domain
    return_url = '%s://%s%s' % (scheme, host, reverse('subscription:paypal-success-response',kwargs={'pk':subscription.id}))
    cancel_url = '%s://%s%s' % (scheme, host, reverse('subscription:paypal-cancel-response'))

    return set_txn(subscription=subscription,
                   currency=currency,
                   return_url=return_url,
                   cancel_url=cancel_url,
                   user=user)


def fetch_transaction_details(token):
    """
    Fetch the completed details about the PayPal transaction.
    """
    return get_txn(token)


def confirm_transaction(subscription, payer_id, token, currency):
    """
    Confirm the payment action.
    """
    return do_txn_recurring(subscription, payer_id, token, currency)
