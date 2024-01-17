from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from djstripe.models import Charge
from djstripe.signals import WEBHOOK_SIGNALS
from djstripe import webhooks
import subscriptions
from subscriptions.utils import send_admin_donation_notification


# @receiver(WEBHOOK_SIGNALS['charge.succeeded'])
@webhooks.handler("charge.succeeded")
def invoice_payment_succeeded(event, **kwargs):
    """Receive notifications from invoice payment (subscriptions)
    and accrue the donation.
    """
    print('Invoice payment ...')
    if event:
        print('here 1')
        customer = event.customer
        charge = event.message['data']['object']
        metadata = charge['metadata']
        if 'isFoundation' in metadata and not metadata['isFoundation']:
            return

        charge_id = charge['id']
        amount = charge['amount'] / 100
        print('here 2')
        donation = subscriptions.models.Donation.objects.filter(reference=charge_id).first()
        print('here 3')
        if not donation:
            print('here 4')
            donation = {
                'user': customer.subscriber,
                'currency': 'USD',
                'payment_source': 'Stripe Subscription',
                'amount': amount,
                'reference': charge_id,
                'confirmed': True,
            }
            if 'sponsored_event_id' in metadata:
                donation['sponsored_event_id'] = metadata['sponsored_event_id']
                donation['sponsored_event_dedication'] = metadata['sponsored_event_dedication']
            print('here 4')
            subscriptions.models.Donation.objects.create(**donation)
            print('here 5')
        else:
            print('here 6')
            print(donation)
            print(donation.id)
            donation.confirmed = True
            donation.save()


# Send email updates to admin only if donation is confirmed
# Strategy: set flag on pre-save if confirmed transitioned to True
# and send email on post_save (when donation is actually confirmed)
# If the flag was set previously, just to avoid duplicates.
@receiver(pre_save, sender='subscriptions.Donation')
def check_admin_update(sender, instance, update_fields=None, **kwargs):
    is_delayed = instance.payment_source == 'Check' or \
                 instance.payment_source == 'BitCoin'
    # Send notification when Donation is created only for check or bitcoin.
    send_email = False
    if not instance.pk:
        send_email = is_delayed

    send_email = send_email and not instance.payment_source == 'Stripe Subscription'

    instance.__send_email = send_email


@receiver(post_save, sender='subscriptions.Donation')
def send_admin_update(sender, instance, created, **kwargs):
    if instance.__send_email:
        send_admin_donation_notification(instance)


#@webhooks.handler("invoice.payment_succeeded")
@receiver(WEBHOOK_SIGNALS['invoice.payment_succeeded'])
def test_webhook(event, **kwargs):
    print('We are here ..')
