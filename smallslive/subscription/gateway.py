import urllib
import logging
from decimal import Decimal as D
from datetime import date
import time
import urlparse
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import exceptions
from models import ExpressTransaction, _TIME_UNIT_CHOICES

logging.basicConfig()

# PayPal methods
SET_EXPRESS_CHECKOUT = 'SetExpressCheckout'
GET_EXPRESS_CHECKOUT_DETAILS = 'GetExpressCheckoutDetails'
CREATE_RECURRING_PAYMENTS_PROFILE = 'CreateRecurringPaymentsProfile'

# It's quite difficult to work out what the latest version of the PayPal
# Express API is.  The best way is to look for the 'web version: ...' string in
# the source of https://www.sandbox.paypal.com/
PAYPAL_API_VERSION = getattr(settings, 'PAYPAL_API_VERSION', '88.0')

PAYPAL_API_USERNAME = getattr(settings, 'PAYPAL_API_USERNAME', 'test')

PAYPAL_API_PASSWORD = getattr(settings, 'PAYPAL_API_PASSWORD', 'test')

PAYPAL_API_SIGNATURE = getattr(settings, 'PAYPAL_API_SIGNATURE', 'test')

PAYPAL_SANDBOX_MODE = getattr(settings, 'PAYPAL_SANDBOX_MODE', True)

logger = logging.getLogger('paypal.express')


def _format_currency(amt):
    return amt.quantize(D('0.01'))


def post(url, params):
    """
    Make a POST request to the URL using the key-value pairs.  Return
    a set of key-value pairs.

    :url: URL to post to
    :params: Dict of parameters to include in post payload
    """
    for k in params.keys():
        if type(params[k]) == unicode:
            params[k] = params[k].encode('utf-8')
    payload = urllib.urlencode(params.items())

    start_time = time.time()
    response = requests.post(url, payload)
    if response.status_code != requests.codes.ok:
        raise exceptions.PayPalError("Unable to communicate with PayPal")

    # Convert response into a simple key-value format
    pairs = {}
    for key, values in urlparse.parse_qs(response.content).items():
        pairs[key] = values[0]

    # Add audit information
    pairs['_raw_request'] = payload
    pairs['_raw_response'] = response.content
    pairs['_response_time'] = (time.time() - start_time) * 1000.0

    return pairs


def _fetch_response(method, extra_params):
    """
    Fetch the response from PayPal and return a transaction object
    """
    # Build parameter string
    params = {
        'METHOD': method,
        'VERSION': PAYPAL_API_VERSION,
        'USER': PAYPAL_API_USERNAME,
        'PWD': PAYPAL_API_PASSWORD,
        'SIGNATURE': PAYPAL_API_SIGNATURE,
    }
    params.update(extra_params)

    if PAYPAL_SANDBOX_MODE:
        url = 'https://api-3t.sandbox.paypal.com/nvp'
    else:
        url = 'https://api-3t.paypal.com/nvp'
    logging.critical(url)
    pairs = post(url, params)

    # Record transaction data - we save this model whether the txn
    # was successful or not
    txn = ExpressTransaction(
        method=method,
        version=PAYPAL_API_VERSION,
        ack=pairs['ACK'],
        raw_request=pairs['_raw_request'],
        raw_response=pairs['_raw_response'],
        response_time=pairs['_response_time'],
    )
    if txn.is_successful:
        txn.correlation_id = pairs['CORRELATIONID']
        if method == SET_EXPRESS_CHECKOUT:
            txn.amount = 0
            txn.token = pairs['TOKEN']
        elif method == GET_EXPRESS_CHECKOUT_DETAILS and pairs['BILLINGAGREEMENTACCEPTEDSTATUS'] == '1':
            txn.profile_id = pairs['PAYERID']
            txn.currency = pairs['CURRENCYCODE']
            txn.token = params['TOKEN']
        elif method == CREATE_RECURRING_PAYMENTS_PROFILE:
            txn.token = params['TOKEN']
            txn.profile_id = pairs['PROFILEID']
            txn.profile_status = pairs['PROFILESTATUS']
    else:
        # There can be more than one error, each with its own number.
        if 'L_ERRORCODE0' in pairs:
            txn.error_code = pairs['L_ERRORCODE0']
        if 'L_LONGMESSAGE0' in pairs:
            txn.error_message = pairs['L_LONGMESSAGE0']
    txn.save()

    if not txn.is_successful:
        msg = "Error %s - %s" % (txn.error_code, txn.error_message)
        logger.error(msg)
        raise exceptions.PayPalError(msg)

    return txn


def set_txn(subscription, currency, return_url, cancel_url, update_url=None,
            user=None):
    """
    Register the transaction with PayPal to get a token which we use in the
    redirect URL.  This is the 'SetExpressCheckout' from their documentation.

    There are quite a few options that can be passed to PayPal to configure this
    request - most are controlled by PAYPAL_* settings.
    """
    # PayPal have an upper limit on transactions.  It's in dollars which is
    # a fiddly to work with.  Lazy solution - only check when dollars are used as
    # the PayPal currency.
    amount = subscription.price
    if currency == 'USD' and amount > 10000:
        raise exceptions.PayPalError('PayPal can only be used for orders up to 10000 USD')

    params = {
        'RETURNURL': return_url,
        'CANCELURL': cancel_url,
        'L_BILLINGTYPE0': 'RecurringPayments',
        'L_BILLINGAGREEMENTDESCRIPTION0': getattr(settings, 'SUBSCRIPTION_DESCRIPTION', 'Website subscription ') + subscription.name
    }

    # Display settings
    page_style = getattr(settings, 'PAYPAL_PAGESTYLE', None)
    header_image = getattr(settings, 'PAYPAL_HEADER_IMG', None)
    if page_style:
        params['PAGESTYLE'] = page_style
    elif header_image:
        params['LOGOIMG'] = header_image
    else:
        # Think these settings maybe deprecated in latest version of PayPal's
        # API
        display_params = {
            'HDRBACKCOLOR': getattr(settings,
                                    'PAYPAL_HEADER_BACK_COLOR', None),
            'HDRBORDERCOLOR': getattr(settings,
                                      'PAYPAL_HEADER_BORDER_COLOR', None),
        }
        params.update(x for x in display_params.items() if bool(x[1]))

    # Locale
    locale = getattr(settings, 'PAYPAL_LOCALE', None)
    if locale:
        valid_choices = ('AU', 'DE', 'FR', 'GB', 'IT', 'ES', 'JP', 'US', 'PL')
        if locale not in valid_choices:
            raise ImproperlyConfigured(
                "'%s' is not a valid locale code" % locale)
        params['LOCALECODE'] = locale

    # Instant update callback information
    if update_url:
        params['CALLBACK'] = update_url
        params['CALLBACKTIMEOUT'] = getattr(
            settings, 'PAYPAL_CALLBACK_TIMEOUT', 3)

    # Contact details and address details - we provide these as it would make
    # the PayPal registration process smoother is the user doesn't already have
    # an account.
    if user:
        params['EMAIL'] = user.email

    txn = _fetch_response(SET_EXPRESS_CHECKOUT, params)

    # Construct return URL
    if PAYPAL_SANDBOX_MODE:
        url = 'https://www.sandbox.paypal.com/webscr'
    else:
        url = 'https://www.paypal.com/webscr'
    params = (('cmd', '_express-checkout'),
              ('token', txn.token),)
    return '%s?%s' % (url, urllib.urlencode(params))


def get_txn(token):
    """
    Fetch details of a transaction from PayPal using the token as
    an identifier.
    """
    return _fetch_response(GET_EXPRESS_CHECKOUT_DETAILS, {'TOKEN': token})


def do_txn_recurring(subscription, payer_id, token, currency):
    """
    CreateRecurringPaymentsProfile
    """
    params = {
        'PAYERID': payer_id,
        'TOKEN': token,
        'PROFILESTARTDATE': date.today().strftime("%Y-%m-%dT%H:%M:%S"),
        'AMT': float(subscription.price or 0.0),
        'CURRENCYCODE': currency,
        'DESC': getattr(settings, 'SUBSCRIPTION_DESCRIPTION', 'Website subscription ') + subscription.name,
        'BILLINGPERIOD': subscription.recurrence_unit,
        'BILLINGFREQUENCY': subscription.recurrence_period,
        'MAXFAILEDPAYMENTS': 3
    }
    if subscription.trial_period:
        params.update({
            'TRIALBILLINGPERIOD': subscription.trial_unit,
            'TRIALBILLINGFREQUENCY': 1,
            'TRIALTOTALBILLINGCYCLES': subscription.trial_period,
            'TRIALAMT':subscription.trial_price
        })

    return _fetch_response(CREATE_RECURRING_PAYMENTS_PROFILE, params)
