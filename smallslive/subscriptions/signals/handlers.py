from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from djstripe.models import Charge
from djstripe.signals import WEBHOOK_SIGNALS
import subscriptions
from subscriptions.utils import send_admin_donation_notification


@receiver(WEBHOOK_SIGNALS['invoice.payment_succeeded'])
def invoice_payment_succeeded(sender, **kwargs):
    """Receive notifications from invoice payment (subscriptions)
    and accrue the donation.
    """
    event = kwargs.get('event')
    if event:
        customer = event.customer
        charge_id = event.message['data']['object']['charge']
        charge = Charge.objects.get(stripe_id=charge_id)
        donation = subscriptions.models.Donation.objects.filter(reference=charge.stripe_id).first()
        if not donation:
            donation = {
                'user': customer.subscriber,
                'currency': 'USD',
                'payment_source': 'Stripe Subscription',
                'amount': charge.amount,
                'reference': charge.stripe_id,
                'confirmed': True,
            }
            subscriptions.models.Donation.objects.create(**donation)


# Send email updates to admin only if donation is confirmed
# Strategy: set flag on pre-save if confirmed transitioned to True
# and send email on post_save (when donation is actually confirmed)
# If the flag was set previously, just to avoid duplicates.
@receiver(pre_save, sender='subscriptions.Donation')
def check_admin_update(sender, instance, update_fields=None, **kwargs):
    is_delayed = instance.payment_source == 'Check' or \
                 instance.payment_source == 'BitCoin'
    if instance.pk:
        old_instance = subscriptions.models.Donation.objects.get(pk=instance.pk)
        # Transition to confirmed
        send_email = not old_instance.confirmed and instance.confirmed and not is_delayed
    else:
        send_email = instance.confirmed or is_delayed

    send_email = send_email and not instance.payment_source == 'Stripe Subscription'

    instance.__send_email = send_email


@receiver(post_save, sender='subscriptions.Donation')
def send_admin_update(sender, instance, created, **kwargs):
    if instance.__send_email:
        send_admin_donation_notification(instance)
