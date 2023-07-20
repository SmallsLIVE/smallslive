import decimal
from datetime import date, timedelta
import stripe
from allauth.account import signals
from allauth.account.adapter import get_adapter
from allauth.account.app_settings import EmailVerificationMethod
from allauth.account.utils import get_login_redirect_url, user_email
from djstripe.models import Customer, Charge, Plan
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils import timezone
from custom_stripe.models import CustomPlan
# from subscriptions.views import update_card

INVOICE_FROM_EMAIL = '' # @TODO Fix later after upgrade dj-stripe 1.2.0 or later

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).
    From StackOverflow
    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


def perform_login(request, user, email_verification,
                  redirect_url=None, signal_kwargs=None,
                  signup=False):
    """
    Overridden from allauth: we needed access to the EmailAddress object and it wasn't
    possible to extend it otherwise. We need to append the 'donate=True' param to
    the confirm email link so that the user can resume donation.

    Keyword arguments:

    signup -- Indicates whether or not sending the
    email is essential (during signup), or if it can be skipped (e.g. in
    case email verification is optional and we are only logging in).
    """

    from .models import SmallsEmailAddress
    has_verified_email = SmallsEmailAddress.objects.filter(user=user,
                                                     verified=True).exists()
    if email_verification == EmailVerificationMethod.NONE:
        pass
    elif email_verification == EmailVerificationMethod.OPTIONAL:
        # In case of OPTIONAL verification: send on signup.
        if not has_verified_email and signup:
            send_email_confirmation(request, user, signup=signup,
                                    activate_view='account_confirm_email')
    elif email_verification == EmailVerificationMethod.MANDATORY:
        if not has_verified_email:
            send_email_confirmation(request, user, signup=signup,
                                    activate_view='account_confirm_email')
            return HttpResponseRedirect('/accounts/confirm-email/')
    # Local users are stopped due to form validation checking
    # is_active, yet, adapter methods could toy with is_active in a
    # `user_signed_up` signal. Furthermore, social users should be
    # stopped anyway.
    if not user.is_active:
        return HttpResponseRedirect(reverse('account_inactive'))
    get_adapter().login(request, user)
    response = HttpResponseRedirect(
        get_login_redirect_url(request, redirect_url))

    if signal_kwargs is None:
        signal_kwargs = {}
    signals.user_logged_in.send(sender=user.__class__,
                                request=request,
                                response=response,
                                user=user,
                                **signal_kwargs)

    return response


def complete_signup(request, user, email_verification, success_url,
                    signal_kwargs=None):
    if signal_kwargs is None:
        signal_kwargs = {}
    signals.user_signed_up.send(sender=user.__class__,
                                request=request,
                                user=user,
                                **signal_kwargs)
    return perform_login(request, user,
                         email_verification=email_verification,
                         signup=True,
                         redirect_url=success_url,
                         signal_kwargs=signal_kwargs)


def send_email_confirmation(request, user, signup=False, **kwargs):
    """
    E-mail verification mails are sent:
    a) Explicitly: when a user signs up
    b) Implicitly: when a user attempts to log in using an unverified
    e-mail while EMAIL_VERIFICATION is mandatory.

    Especially in case of b), we want to limit the number of mails
    sent (consider a user retrying a few times), which is why there is
    a cooldown period before sending a new mail.
    """
    from .models import SmallsEmailAddress, SmallsEmailConfirmation

    COOLDOWN_PERIOD = timedelta(minutes=3)
    email = user_email(user)
    if email:
        try:
            email_address = SmallsEmailAddress.objects.get(
                user=user, email__iexact=email)
            if not email_address.verified:
                send_email = not SmallsEmailConfirmation.objects \
                    .filter(sent__gt=timezone.now() - COOLDOWN_PERIOD,
                            email_address=email_address) \
                    .exists()
                if send_email:
                    email_address.send_confirmation(
                        request,
                        signup=signup,
                        activate_view=kwargs.get('activate_view'))

        except SmallsEmailAddress.DoesNotExist:
            email_address = SmallsEmailAddress.objects.add_email(
                request, user, email, signup=signup, confirm=True)
            assert email_address

    if signup:
        request.session['account_user'] = user.pk


def send_email_confirmation_for_celery(request, user, signup=False, **kwargs):
    """
    Customized send confirmation function that doesn't set (notification) messages and other
    things that depend on the request object since we're passing a mock request object to it.
    """
    from .models import SmallsEmailAddress, SmallsEmailConfirmation

    COOLDOWN_PERIOD = timedelta(minutes=3)
    email = user_email(user)
    if email:
        try:
            email_address = SmallsEmailAddress.objects.get(
                user=user, email__iexact=email)
            if not email_address.verified:
                send_email = not SmallsEmailConfirmation.objects \
                    .filter(sent__gt=timezone.now() - COOLDOWN_PERIOD,
                            email_address=email_address) \
                    .exists()
                if send_email:
                    email_address.send_confirmation(
                        request,
                        signup=signup,
                        activate_view=kwargs.get('activate_view'))
            else:
                send_email = False
        except SmallsEmailAddress.DoesNotExist:
            send_email = True
            email_address = SmallsEmailAddress.objects.add_email(
                request, user, email, signup=signup, confirm=True)
            assert email_address


def one_time_donation(customer, stripe_token, amount, donation_type='one_time',
                      event_id=None, dedication='', musician='', event_date=''):

    #customer.update_card(stripe_token) # @TODO: Figure out update_card later.
    if event_id:
        metadata = {
            'sponsored_event_id': event_id,
            'sponsored_event_dedication': dedication
        }
    else:
        metadata = {}
    charge_object = charge(customer, amount, send_receipt=False, metadata=metadata, token=stripe_token)
    custom_receipt = {
        'customer': customer,
        'amount': amount,
        'type': donation_type,
    }
    custom_send_receipt(receipt_info=custom_receipt, dedication=dedication,
                        musician=musician, event_date=event_date, user=customer.subscriber)

    return charge_object.stripe_id


def update_active_card(customer, stripe_token):
    customer.update_card(stripe_token)


def subscribe_to_plan(customer, stripe_token, amount, plan_type,
                      flow="Charge"):
    plan_data = {
        'amount': amount,
        'currency': 'usd',
        'interval': plan_type,
    }

    plan = Plan.objects.filter(**plan_data).first()
    plan_data['product'] = settings.STRIPE_PRODUCT
    plan = plan or CustomPlan.create(**plan_data)

    #customer.update_card(stripe_token)
    charge_id = subscribe(customer, plan, flow, plan_data, stripe_token)
    custom_receipt = {}
    custom_receipt['customer'] = customer
    custom_receipt['plan'] = plan
    custom_receipt['type'] = 'subscribe'
    custom_send_receipt(receipt_info=custom_receipt)
    return charge_id

    # Donation will come through Stripe's webhook


def subscribe(customer, plan, flow, plan_data, stripe_token):

    #cu = customer.stripe_customer
    cu = customer.api_retrieve()
    #customer.update_subscription(plan=plan.stripe_id, prorate=False)
    try:
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "token": stripe_token,
            },
        )
        
        stripe.PaymentMethod.attach(
            payment_method.id,
            customer=customer.stripe_id,
        )

        current_subscription = stripe.Subscription.create(
            customer=customer.stripe_id,
            items=[{
                'price': plan.stripe_id,
            }],
            default_payment_method= payment_method.id
        )

        subscription = stripe.Subscription.retrieve(current_subscription.id)
        latest_invoice_id = subscription.latest_invoice
        invoice = stripe.Invoice.retrieve(latest_invoice_id)
        charge_id = invoice.charge
        return charge_id

        #current_subscription = customer.subscribe(plan.stripe_id)
        # current_subscription.plan = plan.stripe_id
        # current_subscription.amount = plan.amount
        # current_subscription.save()
        
                
    except Exception as e:
        print(e)
        sub = cu.subscription

        # @TODO - FIX this after migrate to dj-stripe 1.20 or later
        # cs = CurrentSubscription.objects.create(
        #     customer=customer,
        #     plan=plan.stripe_id,
        #     current_period_start=convert_tstamp(sub.current_period_start),
        #     current_period_end=convert_tstamp(sub.current_period_end),
        #     amount=sub.plan.amount,
        #     status=sub.status,
        #     cancel_at_period_end=sub.cancel_at_period_end,
        #     canceled_at=convert_tstamp(sub, 'canceled_at'),
        #     start=convert_tstamp(sub.start),
        #     quantity=sub.quantity)
        #
        # return cs
        return sub


def charge(customer, amount, currency='USD', description='',
           send_receipt=True, metadata={},token=None):
    """Just charge the customer
    The web hook will take care of updating donations if necessary"""
    source = stripe.Source.create(
        type='card',
        amount=int(decimal.Decimal(amount) * 100),
        currency=currency,
        owner={
        'email': customer.subscriber.email
        },
        token=token
    )
    resp = stripe.Charge.create(
        amount=int(decimal.Decimal(amount) * 100),  # Convert dollars into cents
        currency=currency,
        customer=customer.stripe_id,
        description=description,
        metadata=metadata,
        source = source.id
    )
    # print(dir(customer))
    # print(resp["id"])
    # obj = customer.record_charge(resp["id"])
    # if send_receipt:
    #     obj.send_receipt()
    

    return resp


def custom_send_receipt(receipt_info={},
                        receipt_type=None, user=None, amount=None,
                        dedication=None, musician=None, event_date=None):

    site = Site.objects.get_current()
    protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
    receipt_type = receipt_info.get('type') or receipt_type
    if receipt_type == 'subscribe':
        user = receipt_info['customer'].subscriber
        ctx = {
            'amount': receipt_info['plan'].amount,
            'user': user,
            'site': site,
            'protocol': protocol,
        }
        subject = render_to_string('djstripe/email/subject.txt', ctx)
        message = render_to_string('djstripe/email/body_base_pledge.txt', ctx)
    elif receipt_type == 'one_time':
        if receipt_info.get('amount'):
            amount = receipt_info['amount']
            user = receipt_info['customer'].subscriber
        ctx = {
            'amount': amount,
            'user': user,
            'site': site,
            'protocol': protocol,
        }
        subject = render_to_string('djstripe/email/subject.txt', ctx)
        message = render_to_string('djstripe/email/body_base_onetime.txt', ctx)
    elif receipt_type == 'gift':
        pass
    elif receipt_type == 'event_sponsorship':
        ctx = {
            'dedication': dedication,
            'musician': musician,
            'event_date': event_date.strftime('%-m/%-d/%y'),
            'user': user,
            'site': site,
            'protocol': protocol,
        }
        subject = render_to_string('djstripe/email/subject.txt', ctx)
        message = render_to_string('djstripe/email/body_base_event_sponsorship.txt', ctx)

    email_to = [user.email]
    subject = subject.strip()
    num_sent = EmailMessage(
        subject,
        message,
        to=email_to,
        bcc=['foundation@smallslive.com'],
        from_email=INVOICE_FROM_EMAIL).send()

    if receipt_info.get('customer'):
        receipt_info['customer'].receipt_sent = num_sent > 0
        receipt_info['customer'].save()


def send_admin_notification(order_number):

    subject = "Order with shipping required received {}".format(order_number)
    message = "Order {} was received and requires shipping".format(order_number)

    email_to = ['foundation@smallslive.com']
    subject = subject.strip()
    EmailMessage(
        subject,
        message,
        to=email_to,
        from_email=INVOICE_FROM_EMAIL).send()

from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.http import base36_to_int
def url_str_to_user_pk(s):
    User = get_user_model()
    # TODO: Ugh, isn't there a cleaner way to determine whether or not
    # the PK is a str-like field?
    if getattr(User._meta.pk, 'remote_field', None):
        pk_field = User._meta.pk.remote_field.to._meta.pk
    else:
        pk_field = User._meta.pk
    if issubclass(type(pk_field), models.UUIDField):
        return pk_field.to_python(s)
    try:
        # pk_field.to_python('a')
        pk = s
    except ValidationError:
        pk = base36_to_int(s)
    return pk
