import decimal
from datetime import timedelta

from djstripe.models import CurrentSubscription, convert_tstamp

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now
from allauth.account.adapter import get_adapter
from allauth.account.utils import user_email
from django.contrib import messages


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
            email_address = SmallsEmailAddress.objects.get(user=user, email__iexact=email)
            if not email_address.verified:
                send_email = not SmallsEmailConfirmation.objects \
                    .filter(sent__gt=now() - COOLDOWN_PERIOD,
                            email_address=email_address) \
                    .exists()
                if send_email:
                    email_address.send_confirmation(request,
                                                    signup=signup, activate_view=kwargs.get('activate_view'))
            else:
                send_email = False
        except SmallsEmailAddress.DoesNotExist:
            send_email = True
            email_address = SmallsEmailAddress.objects.add_email(request,
                                                           user,
                                                           email,
                                                           signup=signup,
                                                           confirm=True)
            assert email_address
        # At this point, if we were supposed to send an email we have sent it.
        if send_email:
            get_adapter().add_message(request,
                                      messages.INFO,
                                      'account/messages/'
                                      'email_confirmation_sent.txt',
                                      {'email': email})
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
            email_address = SmallsEmailAddress.objects.get(user=user, email__iexact=email)
            if not email_address.verified:
                send_email = not SmallsEmailConfirmation.objects \
                    .filter(sent__gt=now() - COOLDOWN_PERIOD,
                            email_address=email_address) \
                    .exists()
                if send_email:
                    email_address.send_confirmation(request,
                                                    signup=signup, activate_view=kwargs.get('activate_view'))
            else:
                send_email = False
        except SmallsEmailAddress.DoesNotExist:
            send_email = True
            email_address = SmallsEmailAddress.objects.add_email(request,
                                                           user,
                                                           email,
                                                           signup=signup,
                                                           confirm=True)
            assert email_address


def subscribe(customer, plan):
    cu = customer.stripe_customer
    cu.update_subscription(plan=plan.stripe_id)
    try:
        current_subscription = customer.current_subscription
        current_subscription.plan = plan.stripe_id
        current_subscription.amount = (plan.amount / decimal.Decimal("100"))
        current_subscription.save()
    except CurrentSubscription.DoesNotExist:
        sub = cu.subscription
        CurrentSubscription.objects.create(
            customer=customer,
            plan=plan.stripe_id,
            current_period_start=convert_tstamp(
                sub.current_period_start
            ),
            current_period_end=convert_tstamp(
                sub.current_period_end
            ),
            amount=(sub.plan.amount / decimal.Decimal("100")),
            status=sub.status,
            cancel_at_period_end=sub.cancel_at_period_end,
            canceled_at=convert_tstamp(sub, "canceled_at"),
            start=convert_tstamp(sub.start),
            quantity=sub.quantity
        )
