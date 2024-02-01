import stripe
import json
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from djstripe.models import Charge
from djstripe.signals import WEBHOOK_SIGNALS
from djstripe import webhooks
import subscriptions
from subscriptions.utils import send_admin_donation_notification


# @receiver(WEBHOOK_SIGNALS['charge.succeeded'])
@webhooks.handler("invoice.payment_succeeded")
def invoice_payment_succeeded(event, **kwargs):
    """Receive notifications from invoice payment (subscriptions)
    and accrue the donation.
    """
    print('Invoice payment ...')
    if event:
        # charge = event.data['object']
        print('==================event ..................')
        print(dir(event))
        print(dir(event.data))

        from pprint import pprint
        print('=====================event data ====')
        pprint(event.data)

        invoice = event.data

        customer = invoice.customer
        metadata = invoice.metadata
        if metadata and 'isFoundation' in metadata and not metadata['isFoundation']:
            return

        charge_id = invoice.charge
        amount = invoice.amount_paid / 100
        donation = subscriptions.models.Donation.objects.filter(reference=charge_id).first()
        if not donation:
            donation = {
                'user': customer.subscriber,
                'currency': 'USD',
                'payment_source': 'Stripe Subscription',
                'amount': amount,
                'reference': charge_id,
                'confirmed': True,
            }
            if metadata and 'sponsored_event_id' in metadata:
                donation['sponsored_event_id'] = metadata['sponsored_event_id']
                donation['sponsored_event_dedication'] = metadata['sponsored_event_dedication']
            subscriptions.models.Donation.objects.create(**donation)
            print('Invoice payment donation created successfully')

            if not customer.default_payment_method:
                print('User have no default payment method')
                payment_intent_id = invoice.payment_intent
                if payment_intent_id:
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                    payment_method = payment_intent.payment_method
                    customer.add_payment_method(payment_method)
                    customer.metadata = json.loads(customer.metadata)
                    customer.invoice_settings = json.loads(customer.invoice_settings)
                    customer.preferred_locales = json.loads(customer.preferred_locales)
                    customer.save()
                print('Successfully added Payment Method')

        else:
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
