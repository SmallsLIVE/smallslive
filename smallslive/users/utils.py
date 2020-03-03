import decimal
from datetime import date, timedelta
from allauth.account import signals
from allauth.account.adapter import get_adapter
from allauth.account.app_settings import EmailVerificationMethod
from allauth.account.utils import get_login_redirect_url, user_email
from djstripe.models import Customer, Charge, CurrentSubscription, convert_tstamp, Plan
from djstripe.settings import PAYMENTS_PLANS, INVOICE_FROM_EMAIL, SEND_INVOICE_RECEIPT_EMAILS
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils import timezone
from custom_stripe.models import CustomPlan


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
            return HttpResponseRedirect(
                reverse('account_email_verification_sent'))
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


def one_time_donation(customer, stripe_token, amount):

    customer.update_card(stripe_token)
    charge_object = charge(customer, amount, send_receipt=False)
    custom_receipt = {
        'customer': customer,
        'amount': amount,
        'type': 'one_time',
    }
    custom_send_receipt(receipt_info=custom_receipt)

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
    # TODO: move this to settings.
    plan_data['product'] = 'prod_D01wWC6DLGhq3U'
    plan = plan or CustomPlan.create(**plan_data)

    customer.update_card(stripe_token)
    subscribe(customer, plan, flow)
    custom_receipt = {}
    custom_receipt["customer"] = customer
    custom_receipt["plan"] = plan
    custom_receipt["type"] = "subscribe"
    custom_send_receipt(receipt_info=custom_receipt)

    # Donation will come through Stripe's webhook


def subscribe(customer, plan, flow):

    cu = customer.stripe_customer
    cu.update_subscription(plan=plan.stripe_id, prorate=False)
    try:
        current_subscription = customer.current_subscription
        current_subscription.plan = plan.stripe_id
        current_subscription.amount = plan.amount
        current_subscription.save()
    except CurrentSubscription.DoesNotExist:
        sub = cu.subscription

        cs = CurrentSubscription.objects.create(
            customer=customer,
            plan=plan.stripe_id,
            current_period_start=convert_tstamp(sub.current_period_start),
            current_period_end=convert_tstamp(sub.current_period_end),
            amount=sub.plan.amount,
            status=sub.status,
            cancel_at_period_end=sub.cancel_at_period_end,
            canceled_at=convert_tstamp(sub, 'canceled_at'),
            start=convert_tstamp(sub.start),
            quantity=sub.quantity)

        return cs


def charge(customer, amount, currency='USD', description='',
           send_receipt=True):
    """Just charge the customer
    The web hook will take care of updating donations if necessary"""

    charge = customer.charge(
        decimal.Decimal(amount), currency, description, send_receipt)

    return charge


def custom_send_receipt(receipt_info={},
                        receipt_type=None, user=None, amount=None):

    site = Site.objects.get_current()
    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    receipt_type = receipt_info.get('type') or receipt_type
    if receipt_type == "subscribe":
        ctx = {
            "amount": receipt_info["plan"].amount,
            "user": receipt_info["customer"].subscriber,
            "site": site,
            "protocol": protocol,
        }
        subject = render_to_string("djstripe/email/subject.txt", ctx)
        message = render_to_string("djstripe/email/body_base_pledge.txt", ctx)
    elif receipt_type == "one_time":
        if receipt_info.get('amount'):
            amount = receipt_info['amount']
            user = receipt_info['customer'].subscriber
        ctx = {
            "amount": amount,
            "user": user,
            "site": site,
            "protocol": protocol,
        }
        subject = render_to_string("djstripe/email/subject.txt", ctx)
        message = render_to_string("djstripe/email/body_base_onetime.txt", ctx)
    elif receipt_type == "gift":
        pass
    subject = subject.strip()
    num_sent = EmailMessage(
        subject,
        message,
        to=[user.email],
        from_email=INVOICE_FROM_EMAIL).send()

    if receipt_info.get('customer'):
        receipt_info["customer"].receipt_sent = num_sent > 0
        receipt_info["customer"].save()



